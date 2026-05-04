FROM python:3.12-alpine AS build

WORKDIR /workspace

ARG SITE_URL
ARG GA4_ID=""
ARG GTM_ID=""
ARG GSC_TOKEN=""

ENV SITE_URL=${SITE_URL}
ENV GA4_ID=${GA4_ID}
ENV GTM_ID=${GTM_ID}
ENV GSC_TOKEN=${GSC_TOKEN}

COPY . .

RUN test -n "${SITE_URL}"
RUN python scripts/build_deploy.py --site-url "${SITE_URL}" --out-dir /workspace/dist

FROM nginx:1.27-alpine AS runtime

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/dist /usr/share/nginx/html

