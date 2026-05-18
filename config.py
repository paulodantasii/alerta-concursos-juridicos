"""Configuração centralizada do CuradorIA / Centralized CuradorIA configuration

Toda constante "ajustável" do projeto vive aqui. Outros módulos importam apenas
do que precisam — não há regra de negócio neste arquivo, só dados.

Every tunable constant of the project lives here. Other modules import only
what they need — no business logic in this file, just data.
"""

# Páginas de listagem que serão raspadas / Listing pages to scrape
TARGET_URLS = [
    "https://www.pciconcursos.com.br/previstos/",
    "https://www.pciconcursos.com.br/noticias/",
    "https://www.pciconcursos.com.br/ultimas/",
    "https://www.acheconcursos.com.br/concursos-atualizados-recentemente",
    "https://www.acheconcursos.com.br/concursos-previstos",
    "https://www.acheconcursos.com.br/concursos-abertos",
]

# Feeds RSS do Google Alerts / Google Alerts RSS feeds
GOOGLE_ALERTS_FEEDS = [
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/13784085206058947900", "term": "seletivo concurso residencia juridica"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/10699205725319407642", "term": "seletivo concurso procurador"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/15459908627525988139", "term": "seletivo concurso advogado"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/5648081314456116013", "term": "seletivo concurso estagio de pos graduacao direito"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/15126815070692715421", "term": "seletivo concurso analista juridico"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/4736851925661048284", "term": "seletivo concurso assessor juridico"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/2563769251380958392", "term": "seletivo concurso tecnico juridico"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/16659093265726736111", "term": "seletivo concurso consultor legislativo"},
    {"url": "https://www.google.com/alerts/feeds/05883152892408713569/4996675272987879500", "term": "seletivo concurso direito"},
]

# Hospedagem / Hosting
GITHUB_USER = "paulodantasii"
GITHUB_REPO = "curadoria-carreiras-juridicas"
REPORT_URL = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/report.html"

# Arquivos / Files
DATABASE_FILE = "database.json"
OUTPUT_NEW_LINKS = "new_links.txt"
OUTPUT_RELEVANT = "new_relevant.txt"
OUTPUT_HTML = "report.html"
HISTORY_DIR = "history"  # Pasta de relatórios datados / Datedreports folder

# Limites e janelas / Limits and windows
MAX_ABSENCES = 3                # Execuções consecutivas sem ver a URL antes de removê-la
MAX_PAGE_CHARS = 7000           # Tamanho máximo do texto enviado à IA
API_PAUSE = 0.1                 # Pausa entre chamadas à OpenAI
BLOCK_403_DAYS = 30             # Bloqueio de domínio após 403
MAX_URL_FAILURES = 3            # Falhas consecutivas antes de aplicar cooldown
URL_COOLDOWN_DAYS = 30          # Duração do cooldown por URL com falhas

# Headers HTTP padrão / Default HTTP headers
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Domínios aceitos no scraping / Accepted scraping domains
TARGET_DOMAINS = {"pciconcursos.com.br", "acheconcursos.com.br"}

# Padrões de URL que classificam um link como notícia / URL patterns that mark a link as news
RELEVANT_PATTERNS = [
    r"/concurso", r"/noticia", r"/edital", r"/concursos/",
    r"/previstos", r"/abertos", r"/autorizados", r"/inscricoes",
    r"/cronograma", r"/ultimas", r"/noticias",
    r"/portal/\d{4}/", r"/portal/[a-z0-9-]+/$",
]

# Padrões de URL que devem ser ignorados / URL patterns to ignore
IGNORE_PATTERNS = [
    r"/(login|cadastro|conta|assinar|assine|newsletter)",
    r"\.(jpg|jpeg|png|gif|pdf|zip|rar|mp4|svg|css|js)$",
    r"/(tag|autor|author|page|pagina)/",
    r"#", r"javascript:", r"mailto:", r"whatsapp:",
]

# Parâmetros de rastreamento removidos das URLs / Tracking parameters stripped from URLs
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "src",
    "mc_cid", "mc_eid", "_hsenc", "_hsmi",
    "li_fat_id", "mkt_tok", "yclid",
    "pk_campaign", "pk_kwd", "pk_source",
    "trk", "trkcampaign", "trkcontent",
}

# Sufixos a remover do final dos títulos / Suffixes to strip from article titles
TITLE_SUFFIXES = [
    " - PCI Concursos", " | PCI Concursos",
    " - JC Concursos", " | JC Concursos",
    " | Folha Dirigida", " - Concursos no Brasil",
    " | Acheconcursos", " - Acheconcursos",
    " - Magistrar", " | Magistrar",
    " - MDC Concursos", " | MDC Concursos",
    " - Estratégia Concursos", " | Estratégia Concursos",
    " - Concurso News", " | Concurso News",
    " - Uniten", " | Uniten", " - G1", " | G1",
    " - Folha PE", " | Folha PE", " - iG", " - iG Economia",
    " - Conjur", " | Conjur", " - Folha Vitória", " | Folha Vitória",
    " - Correio Braziliense", " - Itatiaia", " | Itatiaia",
    " - Mídia Bahia", " | Mídia Bahia", " - Roraima na Rede",
    " - Portal Piauí Hoje", " - Tribuna Online", " - ND Mais", " | ND Mais",
]

# Rótulos visuais para cada carreira jurídica / Visual labels per legal career
CAREER_LABELS = {
    "tribunais": ("Tribunais", "#4B0082"),
    "mp": ("Ministério Público", "#B22222"),
    "defensoria": ("Defensoria Pública", "#104E8B"),
    "procuradorias": ("Procuradorias", "#8B4513"),
    "policiais": ("Carreiras Policiais", "#2F4F4F"),
    "cartorios": ("Cartórios e Notas", "#8B008B"),
    "administrativo": ("Administrativo e Seletivo", "#B8860B"),
    "estagio": ("Residência e Estágio", "#228B22"),
}
