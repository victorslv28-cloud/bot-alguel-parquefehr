import os
import json
import logging
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Telegram Config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Credenciais do Telegram não configuradas. Mensagem não enviada.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem pro Telegram: {e}")
        return False

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Definir os sites e suas URLs de busca
SITES = [
    {
        "name": "Center Imóveis",
        "url": "https://centerimoveis.com/alugar/parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://centerimoveis.com"
    },
    {
        "name": "Roca Imóveis",
        "url": "https://roca.com.br/alugar/parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://roca.com.br"
    },
    {
        "name": "Maria Aires",
        "url": "https://mariaaires.com.br/alugar/parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://mariaaires.com.br"
    },
    {
        "name": "Abias Imóveis",
        "url": "https://abiasimoveis.com.br/aluguel/residencial_comercial/sao-carlos/parque-fehr/",
        "link_pattern": "/imovel/",
        "base_url": "https://abiasimoveis.com.br"
    },
    {
        "name": "Cia do Imóvel",
        "url": "https://www.ciadoimovelsaocarlos.com.br/pesquisa-de-imoveis/?locacao_venda=L&id_cidade%5B%5D=190&id_bairro%5B%5D=3742&finalidade=0&dormitorio=0&garagem=0&vmi=&vma=",
        "link_pattern": "/pesquisa-de-imoveis/alugar/Sao-Carlos/",
        "base_url": "https://www.ciadoimovelsaocarlos.com.br"
    },
    {
        "name": "iPlano Imóveis",
        "url": "https://iplano.com.br/alugar/parque-fehr-sao-carlos-sp,residencial-parque-fehr-sao-carlos-sp/casas",
        "link_pattern": "/imovel/",
        "base_url": "https://iplano.com.br"
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

def is_valid_house_link(href, text):
    href_lower = href.lower()
    text_lower = text.lower()
    
    # Excluir apartamentos e terrenos explicitamente
    if 'apartamento' in href_lower or 'apartamento' in text_lower:
        return False
    if 'apto' in href_lower or 'apto ' in text_lower:
        return False
    if 'terreno' in href_lower or 'terreno' in text_lower:
        return False
    if 'lote' in href_lower or 'lote' in text_lower:
        return False
        
    # Verificar se as palavras "casa" ou "sobrado" estao no texto ou URL
    if 'casa' in href_lower or 'casa' in text_lower or 'sobrado' in href_lower or 'sobrado' in text_lower:
        return True
        
    # Se não fala nada, ignora na duvida, mas como buscamos casas, melhor ser estrito
    return False

def scrape_site(site_config):
    logging.info(f"Buscando em {site_config['name']}...")
    houses_found = []
    try:
        response = requests.get(site_config["url"], headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar todos os links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            
            if site_config["link_pattern"] in href:
                full_link = href if href.startswith('http') else site_config["base_url"] + href
                
                # Ignorar links de paginação, etc, garantindo que tenham id numerico geralmente
                if is_valid_house_link(href, text):
                    # Evitar duplicatas exatas na lista
                    if not any(h['link'] == full_link for h in houses_found):
                        houses_found.append({
                            "site": site_config["name"],
                            "title": text,
                            "link": full_link
                        })
    except Exception as e:
        logging.error(f"Erro ao buscar em {site_config['name']}: {e}")
        
    return houses_found

def get_all_houses():
    all_houses = []
    for site in SITES:
        houses = scrape_site(site)
        all_houses.extend(houses)
        logging.info(f"-> {len(houses)} casas encontradas em {site['name']}")
    return all_houses

STATE_FILE = "imoveis.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_state(state_data):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Load previously seen houses
    seen_links = load_state()
    
    # Check if first run by verifying if we have no saved houses
    is_first_run = len(seen_links) == 0
    
    if is_first_run:
        welcome_msg = "🤖 <b>Bot de Aluguel Iniciado!</b>\n\nAcabei de ser implantado no servidor e fiz minha primeira varredura com sucesso. A partir de agora, te avisarei aqui sempre que uma casa nova surgir no Parque Fehr!"
        send_telegram_message(welcome_msg)
        logging.info("Mensagem de primeira execução enviada pro Telegram.")
        
    houses = get_all_houses()
    
    new_houses = []
    for h in houses:
        if h['link'] not in seen_links:
            new_houses.append(h)
            seen_links.append(h['link'])
            
    print(f"\nTotal de casas encontradas na busca atual: {len(houses)}")
    print(f"Total de casas NOVAS encontradas: {len(new_houses)}")
    
    for h in new_houses:
        msg = f"🏠 <b>Nova casa encontrada!</b>\n\n📌 <b>Imobiliária:</b> {h['site']}\n📝 <b>Título:</b> {h['title']}\n🔗 <a href='{h['link']}'>Link do Imóvel</a>"
        print(f"[NOVA] [{h['site']}] {h['title']} - {h['link']}")
        send_telegram_message(msg)
        
    # Save updated state
    save_state(seen_links)
