const header = document.querySelector(".site-header");
const menuToggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelectorAll(".site-nav a");
const samePageAnchors = document.querySelectorAll('a[href^="#"]');
const revealItems = document.querySelectorAll(".reveal");
const year = document.getElementById("year");
const contentFeeds = document.querySelectorAll("[data-content-feed]");
const contentConfig = window.CONNECT_CONTENT_CONFIG || {};
const quoteForm = document.querySelector("[data-quote-form]");
const savingsCalculators = document.querySelectorAll("[data-savings-calculator]");
const sectionNavLinks = document.querySelectorAll("[data-section-nav] a[href^='#']");
const whatsappLinks = document.querySelectorAll('a[href*="wa.me"]');

const fallbackContent = [
  {
    type: "obra",
    title: "Projeto residencial para reduzir custo fixo da família",
    summary:
      "Leitura de fatura, consumo médio e área disponível para uma proposta objetiva, com economia estimada e fornecedores definidos por critério técnico.",
    date: "2026-04-30",
    tag: "Residencial",
    location: "Curitiba/PR",
    image: "assets/images/solar-obra-residencial.webp",
    link: "index.html#contato"
  },
  {
    type: "obra",
    title: "Sistema comercial para dar previsibilidade ao caixa",
    summary:
      "Estudo para negócio com consumo recorrente, buscando reduzir despesa mensal e comparar o investimento com o retorno esperado.",
    date: "2026-04-26",
    tag: "Comercial",
    location: "Região Metropolitana de Curitiba",
    image: "assets/images/solar-obra-comercial.webp",
    link: "index.html#contato"
  },
  {
    type: "obra",
    title: "Atendimento rural com foco em demanda produtiva",
    summary:
      "Dimensionamento considerando rotina de produção, estabilidade de energia, sazonalidade de consumo e necessidade de suporte próximo.",
    date: "2026-04-22",
    tag: "Rural",
    location: "São Francisco do Sul/SC",
    image: "assets/images/solar-obra-rural.webp",
    link: "index.html#contato"
  },
  {
    type: "obra",
    title: "Pequena indústria avaliando geração própria",
    summary:
      "Análise para operação leve que precisa reduzir o peso da energia no custo produtivo sem perder clareza sobre prazo, marcas e implantação.",
    date: "2026-04-18",
    tag: "Indústria",
    location: "Paraná",
    image: "assets/images/solar-obra-comercial.webp",
    link: "index.html#contato"
  },
  {
    type: "informativo",
    title: "Como comparar um orçamento solar sem olhar só para o preço",
    summary:
      "Preço importa, mas a decisão precisa considerar dimensionamento, marcas, garantia, homologação, prazo, financiamento e pós-venda.",
    date: "2026-04-29",
    tag: "Guia de compra",
    link: "blog.html"
  },
  {
    type: "informativo",
    title: "Por que enviar a fatura de energia antes do orçamento",
    summary:
      "A conta de luz mostra consumo, tarifa e histórico. Sem ela, qualquer estimativa de economia fica genérica demais para uma boa decisão.",
    date: "2026-04-27",
    tag: "Dúvidas frequentes",
    link: "blog.html"
  },
  {
    type: "informativo",
    title: "Marcas fortes aumentam segurança no projeto",
    summary:
      "BYD, WEG, BelEnergy e JNG entram na conversa porque desempenho, assistência e disponibilidade também fazem parte do investimento.",
    date: "2026-04-24",
    tag: "Fornecedores",
    link: "blog.html"
  },
  {
    type: "informativo",
    title: "O que esperar da homologação do sistema solar",
    summary:
      "Depois da aprovação, o projeto passa por visita técnica, pagamento, entrega do kit, instalação, homologação na Copel ou Celesc e sistema funcionando.",
    date: "2026-04-20",
    tag: "Processo",
    link: "blog.html"
  }
];

const syncHeaderState = () => {
  if (window.scrollY > 12) {
    header.classList.add("is-scrolled");
  } else {
    header.classList.remove("is-scrolled");
  }

  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? `${(window.scrollY / scrollable) * 100}%` : "0%";
  document.documentElement.style.setProperty("--scroll-progress", progress);
};

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    menuToggle.setAttribute("aria-label", expanded ? "Abrir menu" : "Fechar menu");
    header.classList.toggle("nav-open", !expanded);
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    header.classList.remove("nav-open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

samePageAnchors.forEach((link) => {
  link.addEventListener("click", (event) => {
    const hash = link.getAttribute("href");
    if (!hash || hash === "#") {
      return;
    }

    const target = document.querySelector(hash);
    if (!target) {
      return;
    }

    event.preventDefault();
    header.classList.remove("nav-open");
    menuToggle?.setAttribute("aria-expanded", "false");

    if (hash === "#topo") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const headerOffset = (header?.offsetHeight || 0) + 18;
    const targetTop = Math.max(target.getBoundingClientRect().top + window.scrollY - headerOffset, 0);
    window.scrollTo({ top: targetTop, behavior: "smooth" });
  });
});

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        const revealGroup = entry.target.parentElement?.querySelectorAll(".reveal");
        if (revealGroup?.length) {
          const groupIndex = Array.from(revealGroup).indexOf(entry.target);
          entry.target.style.animationDelay = `${Math.min(groupIndex * 90, 280)}ms`;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15 }
  );

  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

if (year) {
  year.textContent = new Date().getFullYear();
}

const trackEvent = (eventName, params = {}) => {
  if (typeof window.gtag === "function") {
    window.gtag("event", eventName, params);
  }
};

whatsappLinks.forEach((link) => {
  link.addEventListener("click", () => {
    trackEvent("whatsapp_click", {
      event_category: "lead",
      link_text: link.textContent.trim() || "WhatsApp"
    });
  });
});

if (quoteForm) {
  quoteForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!quoteForm.reportValidity()) {
      return;
    }

    const data = new FormData(quoteForm);
    const message = [
      "Olá, Connect Energia Solar. Quero uma análise inicial para energia solar.",
      "",
      `Nome: ${data.get("name")}`,
      `Cidade/UF: ${data.get("city")}`,
      `Perfil: ${data.get("profile")}`,
      `Valor médio da conta: ${data.get("bill") || "não informado"}`,
      `Melhor horário: ${data.get("period") || "sem preferência"}`,
      `Tenho fatura para enviar: ${data.get("hasBill") ? "sim" : "ainda não"}`,
      "",
      "Podem me orientar sobre economia, dimensionamento, visita técnica e próximos passos?"
    ].join("\n");

    trackEvent("quote_form_submit", {
      event_category: "lead",
      project_profile: data.get("profile") || "nao_informado"
    });

    window.open(`https://wa.me/5541998641771?text=${encodeURIComponent(message)}`, "_blank", "noopener");
  });
}

const moneyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0
});

const readSavingsEstimate = (calculator) => {
  const data = new FormData(calculator);
  const monthlyBill = Math.max(Number(data.get("monthlyBill")) || 0, 0);
  const reduction = Math.min(Math.max(Number(data.get("reduction")) || 80, 0), 95);
  const monthlySaving = monthlyBill * (reduction / 100);
  const yearlySaving = monthlySaving * 12;

  return { monthlyBill, reduction, monthlySaving, yearlySaving };
};

const renderSavingsEstimate = (calculator) => {
  const estimate = readSavingsEstimate(calculator);
  const monthlyText = moneyFormatter.format(estimate.monthlySaving);
  const yearlyText = moneyFormatter.format(estimate.yearlySaving);

  calculator.querySelectorAll("[data-saving-month]").forEach((item) => {
    item.textContent = item.tagName === "SMALL" ? `${monthlyText}/mês` : monthlyText;
  });

  calculator.querySelectorAll("[data-saving-year]").forEach((item) => {
    item.textContent = yearlyText;
  });

  return estimate;
};

savingsCalculators.forEach((calculator) => {
  const updateEstimate = () => renderSavingsEstimate(calculator);
  updateEstimate();

  calculator.addEventListener("input", updateEstimate);
  calculator.addEventListener("change", updateEstimate);
  calculator.querySelectorAll("input, select").forEach((field) => {
    field.addEventListener("focus", () => {
      calculator.classList.add("is-editing");
    });
  });

  calculator.addEventListener("submit", (event) => {
    event.preventDefault();
    const estimate = renderSavingsEstimate(calculator);
    const context = calculator.dataset.calculatorContext || "simulador";
    const message = [
      "Olá, Connect Energia Solar. Fiz uma prévia de desconto no site e quero uma análise.",
      "",
      `Valor médio da conta: ${moneyFormatter.format(estimate.monthlyBill)}`,
      `Desconto simulado: ${estimate.reduction}%`,
      `Desconto mensal estimado: ${moneyFormatter.format(estimate.monthlySaving)}`,
      `Desconto anual estimado: ${moneyFormatter.format(estimate.yearlySaving)}`,
      "",
      "Podem validar essa estimativa pela minha fatura e orientar os próximos passos?"
    ].join("\n");

    trackEvent("savings_calculator_submit", {
      event_category: "lead",
      calculator_context: context,
      reduction: estimate.reduction
    });

    window.open(`https://wa.me/5541998641771?text=${encodeURIComponent(message)}`, "_blank", "noopener");
  });
});

if (sectionNavLinks.length && "IntersectionObserver" in window) {
  const sectionMap = new Map(
    Array.from(sectionNavLinks)
      .map((link) => {
        const section = document.querySelector(link.getAttribute("href"));
        return section ? [section.id, link] : null;
      })
      .filter(Boolean)
  );

  const activateSectionLink = (id) => {
    sectionNavLinks.forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
    });
  };

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const visibleEntry = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (visibleEntry && sectionMap.has(visibleEntry.target.id)) {
        activateSectionLink(visibleEntry.target.id);
      }
    },
    {
      rootMargin: "-25% 0px -58% 0px",
      threshold: [0.12, 0.3, 0.55]
    }
  );

  sectionMap.forEach((link, id) => {
    document.getElementById(id)?.setAttribute("data-guide-section", "");
    sectionObserver.observe(document.getElementById(id));
  });
}

sectionNavLinks.forEach((link) => {
  link.addEventListener("click", () => {
    trackEvent("site_guide_click", {
      event_category: "navigation",
      section: link.dataset.trackSection || link.getAttribute("href")?.replace("#", "")
    });
  });
});

const normalizeKey = (key) =>
  String(key || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "");

const normalizeType = (value) => {
  const type = normalizeKey(value);
  if (["obra", "obras", "nova_obra", "projeto"].includes(type)) return "obra";
  if (["informativo", "informativos", "aviso", "noticia", "post"].includes(type)) {
    return "informativo";
  }
  return type || "informativo";
};

const parseCsv = (csvText) => {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let i = 0; i < csvText.length; i += 1) {
    const char = csvText[i];
    const next = csvText[i + 1];

    if (char === '"' && quoted && next === '"') {
      field += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") i += 1;
      row.push(field);
      if (row.some((cell) => cell.trim() !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  row.push(field);
  if (row.some((cell) => cell.trim() !== "")) rows.push(row);
  return rows;
};

const mapContentRows = (rows) => {
  if (!rows.length) return [];

  const headers = rows[0].map(normalizeKey);
  return rows.slice(1).map((row) => {
    const source = {};
    headers.forEach((header, index) => {
      source[header] = (row[index] || "").trim();
    });

    return {
      type: normalizeType(source.tipo || source.type || source.categoria),
      title: source.titulo || source.title || source.nome,
      summary: source.resumo || source.summary || source.descricao || source.texto,
      date: source.data || source.date || source.publicado_em,
      tag: source.tag || source.categoria || source.assunto,
      location: source.local || source.cidade || source.location,
      image: source.imagem || source.image || source.foto,
      link: source.link || source.url,
      status: normalizeKey(source.status || "publicado")
    };
  });
};

const normalizeContent = (items) =>
  items
    .map((item) => ({
      type: normalizeType(item.type || item.tipo || item.categoria),
      title: item.title || item.titulo || item.nome,
      summary: item.summary || item.resumo || item.descricao || item.texto,
      date: item.date || item.data || item.publicado_em,
      tag: item.tag || item.categoria || item.assunto,
      location: item.location || item.local || item.cidade,
      image: item.image || item.imagem || item.foto,
      link: item.link || item.url,
      status: normalizeKey(item.status || "publicado")
    }))
    .filter((item) => item.title && item.summary && item.status !== "rascunho");

const formatDate = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).format(date);
};

const renderContentCard = (item) => {
  const article = document.createElement("article");
  article.className = "content-card";

  const href = item.link || (item.type === "obra" ? "index.html#contato" : "blog.html");
  const action = item.type === "obra" ? "Ver obra" : "Ler informativo";
  const meta = [item.location, formatDate(item.date)].filter(Boolean).join(" | ");

  if (item.image) {
    const media = document.createElement("div");
    const image = document.createElement("img");
    media.className = "content-card-media";
    image.src = item.image;
    image.alt = "";
    image.loading = "lazy";
    media.appendChild(image);
    article.appendChild(media);
  }

  const body = document.createElement("div");
  const tagRow = document.createElement("div");
  const tag = document.createElement("span");
  const title = document.createElement("h3");
  const summary = document.createElement("p");
  const link = document.createElement("a");

  body.className = "content-card-body";
  tagRow.className = "post-tag-row";
  tag.className = "blog-preview-tag";
  tag.textContent = item.tag || (item.type === "obra" ? "Nova obra" : "Informativo");
  tagRow.appendChild(tag);

  if (meta) {
    const metaEl = document.createElement("span");
    metaEl.className = "post-meta";
    metaEl.textContent = meta;
    tagRow.appendChild(metaEl);
  }

  title.textContent = item.title;
  summary.textContent = item.summary;
  link.className = "post-link";
  link.href = href;
  link.textContent = action;

  body.append(tagRow, title, summary, link);
  article.appendChild(body);

  return article;
};

const renderContentFeeds = (items) => {
  contentFeeds.forEach((feed) => {
    const type = feed.dataset.contentFeed || "all";
    const limit = Number(feed.dataset.limit || 3);
    const scopedItems = items
      .filter((item) => type === "all" || item.type === type)
      .sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
      .slice(0, limit);

    feed.innerHTML = "";
    scopedItems.forEach((item) => feed.appendChild(renderContentCard(item)));

    if (!scopedItems.length) {
      feed.innerHTML = '<p class="content-empty">As próximas publicações aparecerão aqui.</p>';
    }
  });
};

const loadDynamicContent = async () => {
  if (!contentFeeds.length) return;

  let items = fallbackContent;

  if (contentConfig.dataUrl) {
    try {
      const response = await fetch(contentConfig.dataUrl, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const text = await response.text();
      let parsed = [];
      if (text.trim().startsWith("{") || text.trim().startsWith("[")) {
        const json = JSON.parse(text);
        parsed = normalizeContent(Array.isArray(json) ? json : json.items || []);
      } else {
        parsed = normalizeContent(mapContentRows(parseCsv(text)));
      }
      if (parsed.length) items = parsed;
    } catch (error) {
      console.warn("Não foi possível carregar o conteúdo do Google. Usando fallback local.", error);
    }
  }

  renderContentFeeds(normalizeContent(items));
};

loadDynamicContent();
syncHeaderState();
window.addEventListener("scroll", syncHeaderState, { passive: true });
