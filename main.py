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
    },
    {
        "name": "Cardinalli",
        "url": "https://www.cardinali.com.br/pesquisa-de-imoveis/?busca_free=&locacao_venda=L&valor_loc_min_input=0&valor_loc_max_input=0&valor_ven_min_input=0&valor_ven_max_input=0&id_cidade%5B%5D=190&id_tipo_imovel%5B%5D=39&id_tipo_imovel%5B%5D=10&id_tipo_imovel%5B%5D=40&id_tipo_imovel%5B%5D=12&id_tipo_imovel%5B%5D=13&id_tipo_imovel%5B%5D=180&id_bairro%5B%5D=3742&dormitorio=&garagem=&finalidade=&a_min=&a_max=&area_tipo=&vmi=&vma=",
        "link_pattern": "/pesquisa-de-imoveis/alugar/Sao-Carlos/",
        "base_url": "https://www.cardinali.com.br"
    },
    {
        "name": "Predial São Carlos",
        "url": "https://predialsaocarlos.com/buscar-anuncios/casa-casa_comercial-casa_de_condominio-para-alugar-em-sao%20carlos-no-bairro-parque%20fehr",
        "link_pattern": "/anuncio/",
        "base_url": "https://predialsaocarlos.com"
    },
    {
        "name": "Sapé Imóveis",
        "url": "https://www.sapeimoveis.com.br/Alugar?tipo=CASA&bairro=PQ+FEHR",
        "link_pattern": "Detalhes?id=",
        "base_url": "https://www.sapeimoveis.com.br"
    },
    {
        "name": "Contato Imóveis",
        "url": "https://www.icontato.com.br/alugar/residencial-parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://www.icontato.com.br"
    },
    {
        "name": "São Carlos Imóveis",
        "url": "https://saocarlosimoveis.com.br/alugar/condominio-parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://saocarlosimoveis.com.br"
    },
    {
        "name": "Top Imóveis",
        "url": "https://topimoveissaocarlos.com.br/alugar/parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://topimoveissaocarlos.com.br"
    },
    {
        "name": "Imobiliária Urbana",
        "url": "https://iurbana.com.br/alugar/parque-fehr-sao-carlos-sp",
        "link_pattern": "/imovel/",
        "base_url": "https://iurbana.com.br"
    },
    {
        "name": "Tati Imóveis",
        "url": "https://tatimoveis.com.br/results.php?finalidade=L&tipo=&cidade=S%C3%A3o+Carlos&bairro=Parque+Fehr&ref=&dormitorios=&vagas=&min=&max=&submit=Pesquisar",
        "link_pattern": "/imovel.php",
        "base_url": "https://tatimoveis.com.br"
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
                full_link = href if href.startswith('http') else site_config["base_url"] + (href if href.startswith('/') else '/' + href)
                
                # Se o texto do link for vazio (comum em "stretched-links"), tenta pegar do pai
                if not text:
                    text = a_tag.parent.get_text(separator=' ', strip=True) if a_tag.parent else "Imóvel"

                
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
        
    # Send status message every time the script runs
    if not is_first_run:
        if len(new_houses) == 0:
            status_msg = f"ℹ️ <b>Varredura Concluída</b>\n\nAcabei de checar os {len(SITES)} sites buscando imóveis no Parque Fehr. Nenhuma casa nova foi encontrada no momento."
        else:
            status_msg = f"✅ <b>Varredura Concluída com Sucesso!</b>\n\nAcabei de checar os {len(SITES)} sites buscando imóveis no Parque Fehr e entreguei as {len(new_houses)} novas casas acima."
        send_telegram_message(status_msg)
        
    # Save updated state
    save_state(seen_links)
