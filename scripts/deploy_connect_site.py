#!/usr/bin/env python3
from __future__ import annotations

import argparse
import posixpath
import shlex
import socket
import time
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parent.parent
HOSTINGER_ENV = Path(r"C:\Users\Windows\nucleo\ecosistema_imobiliaria\ops\local\hostinger.env")
SSH_ENV = Path(r"C:\Users\Windows\nucleo\ecosistema_imobiliaria\n8n\.env.local")
REMOTE_ROOT = "/root/connectenergiasolar"
REMOTE_SITE = f"{REMOTE_ROOT}/site"
REMOTE_NGINX = f"{REMOTE_ROOT}/nginx.conf"
REMOTE_TRAEFIK = "/etc/easypanel/traefik/config/connectenergiasolar.yaml"
SERVICE_NAME = "connectenergiasolar_site"
NETWORK_NAME = "easypanel"


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def ssh_connect(host_override: str = "") -> paramiko.SSHClient:
    host_env = load_env(HOSTINGER_ENV)
    ssh_env = load_env(SSH_ENV)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    kwargs: dict[str, object] = {
        "hostname": host_override or host_env["HOSTINGER_VPS_HOST"],
        "username": "root",
        "timeout": 20,
    }

    ssh_key = ssh_env.get("SSH_KEY_PATH", "")
    ssh_pass = ssh_env.get("SSH_PASS", "")

    if ssh_key and Path(ssh_key).exists():
        kwargs["key_filename"] = ssh_key
    elif ssh_pass:
        kwargs["password"] = ssh_pass
    else:
        default_key = Path.home() / ".ssh" / "imobideploy"
        if default_key.exists():
            kwargs["key_filename"] = str(default_key)

    client.connect(**kwargs)
    return client


def run(client: paramiko.SSHClient, command: str, check: bool = True) -> tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    if check and code != 0:
        raise RuntimeError(f"Remote command failed ({code}): {command}\nSTDERR:\n{err}")
    return code, out, err


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    parts = [part for part in remote_dir.split("/") if part]
    current = "/"
    for part in parts:
        current = posixpath.join(current, part)
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def upload_file(sftp: paramiko.SFTPClient, local_path: Path, remote_path: str) -> None:
    ensure_remote_dir(sftp, posixpath.dirname(remote_path))
    sftp.put(str(local_path), remote_path)


def upload_tree(sftp: paramiko.SFTPClient, local_dir: Path, remote_dir: str) -> None:
    ensure_remote_dir(sftp, remote_dir)
    for path in sorted(local_dir.rglob("*")):
        rel = path.relative_to(local_dir).as_posix()
        remote_path = posixpath.join(remote_dir, rel)
        if path.is_dir():
            ensure_remote_dir(sftp, remote_path)
        else:
            upload_file(sftp, path, remote_path)


def write_remote_text(sftp: paramiko.SFTPClient, remote_path: str, content: str) -> None:
    ensure_remote_dir(sftp, posixpath.dirname(remote_path))
    with sftp.open(remote_path, "w") as handle:
        handle.write(content)


def traefik_config(domain: str) -> str:
    return f"""http:
  routers:
    http-connectenergiasolar:
      service: connectenergiasolar-site
      rule: Host(`{domain}`) && PathPrefix(`/`)
      priority: 0
      middlewares:
        - redirect-to-https
        - bad-gateway-error-page
      entryPoints:
        - http
    https-connectenergiasolar:
      service: connectenergiasolar-site
      rule: Host(`{domain}`) && PathPrefix(`/`)
      priority: 0
      middlewares:
        - bad-gateway-error-page
      tls:
        certResolver: letsencrypt
        domains:
          - main: {domain}
      entryPoints:
        - https
  services:
    connectenergiasolar-site:
      loadBalancer:
        servers:
          - url: http://{SERVICE_NAME}:80/
        passHostHeader: true
"""


def wait_for_port(host: str, port: int, timeout_seconds: int = 120) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            sock.connect((host, port))
            sock.close()
            return True
        except OSError:
            time.sleep(2)
        finally:
            sock.close()
    return False


def service_exists(client: paramiko.SSHClient) -> bool:
    code, _, _ = run(client, f"docker service inspect {SERVICE_NAME}", check=False)
    return code == 0


def deploy_service(client: paramiko.SSHClient) -> None:
    base_create = (
        f"docker service create --name {SERVICE_NAME} "
        f"--network {NETWORK_NAME} "
        f"--mount type=bind,src={REMOTE_SITE},dst=/usr/share/nginx/html,ro "
        f"--mount type=bind,src={REMOTE_NGINX},dst=/etc/nginx/conf.d/default.conf,ro "
        f"--label keep=true "
        f"nginx:1.27-alpine"
    )
    if service_exists(client):
        run(client, f"docker service update --force --image nginx:1.27-alpine {SERVICE_NAME}")
    else:
        run(client, base_create)


def verify_remote(client: paramiko.SSHClient, domain: str) -> tuple[str, str]:
    _, http_out, _ = run(
        client,
        f"curl -I -H {shlex.quote(f'Host: {domain}')} http://127.0.0.1 --max-time 20",
        check=False,
    )
    _, https_out, _ = run(
        client,
        f"curl -k -I https://{domain} --max-time 20",
        check=False,
    )
    return http_out, https_out


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Connect Energia Solar site to VPS.")
    parser.add_argument("--domain", default="connectenergiasolar.mpbg.cloud")
    parser.add_argument("--dist-dir", default="dist-connect-live")
    parser.add_argument("--host", default="", help="Optional SSH host override")
    args = parser.parse_args()

    dist_dir = (ROOT / args.dist_dir).resolve()
    if not dist_dir.exists():
        raise SystemExit(f"Dist directory not found: {dist_dir}")

    client = ssh_connect(args.host)
    sftp = client.open_sftp()
    try:
        run(client, f"mkdir -p {REMOTE_SITE}")
        upload_tree(sftp, dist_dir, REMOTE_SITE)
        upload_file(sftp, ROOT / "deploy" / "nginx.conf", REMOTE_NGINX)
        write_remote_text(sftp, REMOTE_TRAEFIK, traefik_config(args.domain))
    finally:
        sftp.close()

    deploy_service(client)
    wait_for_port(load_env(HOSTINGER_ENV)["HOSTINGER_VPS_HOST"], 443, 30)
    time.sleep(8)
    http_out, https_out = verify_remote(client, args.domain)
    client.close()

    print("HTTP check:")
    print(http_out.strip())
    print("\nHTTPS check:")
    print(https_out.strip())


if __name__ == "__main__":
    main()
