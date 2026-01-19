import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
from collections import defaultdict
from typing import Dict, List, Set
import json

# ==================== CONFIGURAÇÃO ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUR_CHAT_ID = os.getenv("YOUR_CHAT_ID", "")  # Configure depois

# CONFIGURAÇÃO DE ALERTAS
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))  # Verifica a cada X minutos
MIN_WALLETS_FOR_ALERT = int(os.getenv("MIN_WALLETS_FOR_ALERT", "2"))   # Alerta quando X+ wallets tiverem o mesmo token

# ==================== SUAS WALLETS ====================
WALLETS = {
  "wuzie": "Bz3mpRUmh79nphvRtJBea1QANbVMVZSN222WdoH6JNTe",
  "gaswhale10": "4hwPamSooBr5JhxHdcEC21HoxN5HUwYR2hGucLPyZAi8",
  "gaswhale6": "7q4v4kQLjU9hW13CQyCwquNBP9LZfbHxPLonHL8TxfyK",
  "Gaswhale5": "S2XVoysKgsZ8ZPaUApxMCdYMjW2SFt8MjLCPwghb5VT",
  "Gaswhale4": "2nKUmHZ3WxQutV9n7GtLYKpMBHud4WMPAzZ4FgWEuHmc",
  "Gaswhale3": "HMMCa4urRGSub1Emotaz5dJbG2YdAD5eEYSAocnpmVmf",
  "Gaswhale1": "4dZBP7udjY8DqvwSGJNyugv2SKs4NfFyCnmC1zCoMPda",
  "won.sol": "DKgvpfttzmJqZXdavDwTxwSVkajibjzJnN2FA99dyciK",
  "SmartMoney": "BieeZkdnBAgNYknzo3RH2vku7FcPkFZMZmRJANh2TpW",
  "smartguy3": "Ehjsi3yYTUZSrTtm7bXduf7usWvodjkcnJCCUHV6ZjQZ",
  "Smartguy2": "HACmcRg4zMFdscJaA2H56fiXC7gqMPhdG3Ypr6umEeyD",
  "Smartguy1": "DBxXDjRdu3JXPN4EfkX4ybymztrEEPAWN743FLDt5HJc",
  "Finn": "BTeqNydtKyDaSxQNRm8ByaUDPK3cpQ1FsXMtaF1Hfaom",
  "CryptoD": "G1pRtSyKuWSjTqRDcazzKBDzqEF96i1xSURpiXj3yFcc",
  "Wolfyxbt": "F7KSBM7SVVYUczJTCLpLJFPDEBrmrfi9ZiGru1BzAuwi",
  "cmem4": "9Ht1BNZP7eTAg5sFtmx4WEEQGXugZMyTQmzdQW6mfvw8",
  "GoatIA": "7qT4fKLKT7kLThgRAq6Lnmq4UPFSq8M3ZeroktMpmBPe",
  "Alon": "6DtEedWf9Wk5hA7Xth82Eq441yf5DA4aGLqaQAVfDokm",
  "profit": "G5nxEXuFMfV74DSnsrSatqCW32F34XUnBeq3PfDS7w5E",
  "Testiclecabal3": "pJRRw7byDh4witgcYsmGm5N7nEJK1Kzo7U39PkbzQUQ",
  "huigendeshen": "Gdaqp3ND6r3HVAWXpawkQU18EuQqwNxpaeeio8ASVAYd",
  "Smart2016": "BC8yiFFQWFEKrEEj75zYsuK3ZDCfv6QEeMRif9oZZ9TW",
  "Asta": "AstaWuJuQiAS3AfqmM3xZxrJhkkZNXtW4VyaGQfqV6JL",
  "Bluechip": "C5tTsPKB9o9Jgqi1SfuwbHY9UHchx5w7VcmCMp5Tmsxu",
  "wechat": "FCkTi9pANbetvGXh73dk6rtSgMz8BoTjRqJMtZ6hxKoV",
  "UranusSwingTrade": "9bVrnS865n4Rwbkjk5NFzDLBiMifJvMNa7e9HDu6DYSb",
  "Insider": "CyHWA7ru59DRzdZASd7EpJFdn5JfuaSSe1Ges6g3XtLD",
  "TesticleCabal2": "3ffMhPbNhmhzZoUqWNKQ2TKsHSg7UpVJAQzB95Ytrrr6",
  "Uranus0": "8VwmbW9VehM9XEc5tLinSAhag8TcrfcMnagmWKEGtxN7",
  "Teep main 🗿": "5VBaSuVdNCHfNwghyaMKauKZpjXVBJNkLE6yVa8PreQj",
  "Mitch 🤡": "4Be9CvxqHW6BYiRAxW9Q3xu1ycTMWaL5z8NX4HR3ha7t",
  "Him": "DxjmHXm1p7cs8Tezdf2EJm5xnwp9QC2E8CbfD1aXeH1j",
  "noob": "NrnKjCKsPMVyyx6yH7oVL8zFciRiBRuxFjdkSm6DR3x",
  "Powside": "CfExiuWfcCzydS3R4YYEcv8W9NUNgcR9xbApjSiDNr6c",
  "Powmain": "8zFZHuSRuDpuAR7J6FzwyF3vKNx4CVW3DFHJerQhc7Zd",
  "Cards": "3DEmhGgQxHsUXq5vLPc7vaiRP2cdJzU9oGDhpCe7n7b4",
  "Snowball": "6N4wVaL7hVtNEU9ACQLv9TCeJk8YJMcRhfqe5Vs7Z3F8",
  "Tom": "AWxr21P2srfkPLiPpqDYyWsKWR1bpJWtw5beVMiRxwZm",
  "PnutWhale": "FjmRj8y9xfDaj5Aygq88t5jAFbpxrbZ16JNPPG1sx9FQ",
  "Remus": "BCrTEXmWutwPz8qv6w1S5gDbaLnSLpXKM5kSGVWyyfxu",
  "Gake_Safe": "EwTNPYTuwxMzrvL19nzBsSLXdAoEmVBKkisN87csKgtt",
  "潜水观察员🇨🇳": "C76PFf7f5M6tMPSaTW8ojFiZiY2tmXHifPYsRzo4KzKx",
  "Zuna 50%": "E4KuDXd8Y4btRksxrjAXMG1xSwcswtph2ZDGrmd5HMRi",
  "王小二": "71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC",
  "Soloxbt": "FTg1gqW7vPm4kdU1LPM7JJnizbgPdRDy2PitKw6mY27j",
  "Uranus1": "5zbQtt1q8zq1SZY4Doc6ct6PP3DhW8cx5S5z2eTcBaMj",
  "Oxsun 100% (KOL)": "HUpPyLU8KWisCAr3mzWy2FKT6uuxQ2qGgJQxyTpDoes5",
  "Oldbutgold": "66uxtTcRJfog5MyU1gsM4kdPYRBsm8LqrJZcA7DTwmYC",
  "Gaswhale9": "ArusEwQvoibSq6oZymxsSrXgzduVuUupDW3iuNqCPNcx",
  "Lmeow": "9yWTCK2Z1HKJuDwJsAQuSsax789AQxWnrQk6b9zpmiQB"
}


# ==================== CLASSES ====================
class TokenInfo:
    def __init__(self, symbol: str, mint: str):
        self.symbol = symbol
        self.mint = mint
        self.wallets_holding: Set[str] = set()
        self.wallet_data: Dict[str, dict] = {}
        self.first_seen = datetime.now()
        self.dex_info: Dict = {}  # Informações extras do DEX
        
    def add_wallet(self, wallet_name: str, amount: float, value_usd: float, buy_price: float = None):
        self.wallets_holding.add(wallet_name)
        self.wallet_data[wallet_name] = {
            'amount': amount,
            'value_usd': value_usd,
            'buy_price': buy_price,
            'current_price': value_usd / amount if amount > 0 else 0,
            'last_updated': datetime.now()
        }
    
    def calculate_pnl(self, wallet_name: str) -> dict:
        if wallet_name not in self.wallet_data:
            return None
        
        data = self.wallet_data[wallet_name]
        if data['buy_price'] and data['buy_price'] > 0:
            pnl = ((data['current_price'] - data['buy_price']) / data['buy_price']) * 100
            return {
                'pnl_percent': pnl,
                'profit': pnl > 0,
                'buy_price': data['buy_price'],
                'current_price': data['current_price']
            }
        return None

class PublicRPCClient:
    def __init__(self):
        self.rpc_url = "https://api.mainnet-beta.solana.com"
        
    async def get_token_accounts(self, wallet_address: str) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        wallet_address,
                        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                        {"encoding": "jsonParsed"}
                    ]
                }
                
                async with session.post(self.rpc_url, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('result', {}).get('value', [])
            except Exception as e:
                print(f"Erro RPC: {e}")
        return []
    
    async def get_token_metadata(self, mint_address: str) -> dict:
        """Busca metadados do token em múltiplas fontes com prioridade"""
        # 1. Tenta DexScreener primeiro (melhor para DEX tokens)
        dex_data = await self._get_dexscreener_data(mint_address)
        if dex_data and dex_data.get('symbol') != 'UNKNOWN':
            return dex_data
        
        # 2. Tenta Jupiter Token List (base de dados estática)
        jupiter_data = await self._get_jupiter_token_info(mint_address)
        if jupiter_data:
            return jupiter_data
        
        # 3. Tenta Solscan público como fallback
        solscan_data = await self._get_solscan_data(mint_address)
        if solscan_data:
            return solscan_data
        
        # 4. Se nada funcionar, retorna dados básicos com o mint
        return {
            'symbol': mint_address[:6],  # Primeiros 6 chars do mint
            'name': f'Token {mint_address[:8]}...',
            'mint': mint_address,
            'source': 'fallback'
        }
    
    async def _get_jupiter_token_info(self, mint_address: str) -> dict:
        """Busca token na lista do Jupiter"""
        async with aiohttp.ClientSession() as session:
            try:
                url = "https://token.jup.ag/strict"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        tokens = await resp.json()
                        for token in tokens:
                            if token.get('address') == mint_address:
                                return {
                                    'symbol': token.get('symbol', 'UNKNOWN'),
                                    'name': token.get('name', ''),
                                    'mint': mint_address,
                                    'source': 'jupiter'
                                }
            except Exception as e:
                print(f"Erro Jupiter Token List: {e}")
        return None
    
    async def _get_solscan_data(self, mint_address: str) -> dict:
        """Busca no Solscan público"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://public-api.solscan.io/token/meta"
                params = {"token": mint_address}
                
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('symbol'):
                            return {
                                'symbol': data.get('symbol', 'UNKNOWN'),
                                'name': data.get('name', ''),
                                'mint': mint_address,
                                'source': 'solscan'
                            }
            except Exception as e:
                print(f"Erro Solscan: {e}")
        return None
    
    async def _get_dexscreener_data(self, mint_address: str) -> dict:
        """Busca dados do DexScreener"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
                
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get('pairs', [])
                        
                        if pairs:
                            # Pega o par com maior liquidez
                            best_pair = max(pairs, key=lambda p: float(p.get('liquidity', {}).get('usd', 0)))
                            
                            symbol = best_pair.get('baseToken', {}).get('symbol', 'UNKNOWN')
                            name = best_pair.get('baseToken', {}).get('name', '')
                            
                            # Se ainda for UNKNOWN, tenta pelo quoteToken
                            if symbol == 'UNKNOWN' or not symbol:
                                symbol = mint_address[:6]
                            
                            return {
                                'symbol': symbol,
                                'name': name if name else f'Token {mint_address[:8]}',
                                'mint': mint_address,
                                'price_usd': float(best_pair.get('priceUsd', 0)),
                                'dex': best_pair.get('dexId', ''),
                                'liquidity': best_pair.get('liquidity', {}).get('usd', 0),
                                'volume_24h': best_pair.get('volume', {}).get('h24', 0),
                                'price_change_24h': best_pair.get('priceChange', {}).get('h24', 0),
                                'url': best_pair.get('url', ''),
                                'pairAddress': best_pair.get('pairAddress', ''),
                                'source': 'dexscreener'
                            }
            except Exception as e:
                print(f"Erro DexScreener: {e}")
        
        return None

class WalletAnalyzer:
    def __init__(self):
        self.rpc_client = PublicRPCClient()
        self.tokens: Dict[str, TokenInfo] = {}
        self.previous_tokens: Dict[str, Set[str]] = {}  # token_mint -> set de wallets que tinham
        self.last_check = datetime.now()
    
    async def analyze_all_wallets(self) -> Dict[str, TokenInfo]:
        """Analisa todas as wallets e detecta NOVOS holders"""
        self.tokens.clear()
        
        for wallet_name, wallet_address in WALLETS.items():
            print(f"Analisando {wallet_name}...")
            await self._analyze_wallet(wallet_name, wallet_address)
        
        self.last_check = datetime.now()
        return self.tokens
    
    def detect_new_holders(self) -> List[tuple]:
        """
        Detecta tokens onde uma NOVA wallet acabou de comprar
        Retorna: lista de (token, nova_wallet, todas_as_wallets_com_esse_token)
        """
        new_holder_alerts = []
        
        for token_mint, token_info in self.tokens.items():
            current_wallets = token_info.wallets_holding
            previous_wallets = self.previous_tokens.get(token_mint, set())
            
            # Detecta wallets que são NOVAS para este token
            new_wallets = current_wallets - previous_wallets
            
            # Se houver pelo menos 1 wallet nova E o token já estava em outra(s) wallet(s)
            if new_wallets and len(previous_wallets) >= 1:
                for new_wallet in new_wallets:
                    # NÃO ignora mais UNKNOWN - vamos mostrar com CA
                    new_holder_alerts.append({
                        'token': token_info,
                        'new_wallet': new_wallet,
                        'all_wallets': current_wallets,
                        'previous_wallets': previous_wallets
                    })
        
        # Atualiza o estado anterior para a próxima verificação
        self.previous_tokens = {
            mint: set(token.wallets_holding) 
            for mint, token in self.tokens.items()
        }
        
        return new_holder_alerts
    
    async def _analyze_wallet(self, wallet_name: str, wallet_address: str):
        token_accounts = await self.rpc_client.get_token_accounts(wallet_address)
        
        for account in token_accounts:
            try:
                parsed = account.get('account', {}).get('data', {}).get('parsed', {})
                info = parsed.get('info', {})
                
                token_mint = info.get('mint')
                amount = float(info.get('tokenAmount', {}).get('uiAmount', 0))
                
                if amount > 0 and token_mint:
                    # Busca metadados (agora com DexScreener)
                    metadata = await self.rpc_client.get_token_metadata(token_mint)
                    
                    symbol = metadata.get('symbol', 'UNKNOWN')
                    
                    # Se veio do DexScreener, já tem preço
                    if metadata.get('source') == 'dexscreener':
                        price = metadata.get('price_usd', 0)
                    else:
                        # Tenta Jupiter como fallback
                        price = await self._get_token_price_jupiter(token_mint)
                    
                    value_usd = amount * price if price else 0
                    
                    if token_mint not in self.tokens:
                        self.tokens[token_mint] = TokenInfo(symbol, token_mint)
                        # Adiciona dados extras do DexScreener
                        if metadata.get('source') == 'dexscreener':
                            self.tokens[token_mint].dex_info = {
                                'name': metadata.get('name', ''),
                                'dex': metadata.get('dex', ''),
                                'liquidity': metadata.get('liquidity', 0),
                                'volume_24h': metadata.get('volume_24h', 0),
                                'price_change_24h': metadata.get('price_change_24h', 0),
                                'url': metadata.get('url', '')
                            }
                    
                    self.tokens[token_mint].add_wallet(
                        wallet_name, 
                        amount, 
                        value_usd,
                        None
                    )
                    
            except Exception as e:
                print(f"Erro ao processar token: {e}")
    
    async def _get_token_price_jupiter(self, token_mint: str) -> float:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://price.jup.ag/v4/price"
                params = {"ids": token_mint}
                
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if token_mint in data.get('data', {}):
                            return float(data['data'][token_mint]['price'])
            except Exception as e:
                print(f"Erro ao buscar preço: {e}")
        return 0.0
    
    def get_new_common_tokens(self, min_wallets: int = 2) -> List[TokenInfo]:
        """DEPRECATED - usar detect_new_holders() ao invés"""
        return []
    
    def mark_as_alerted(self, token_mint: str):
        """DEPRECATED - não precisa mais"""
        pass
    
    def get_common_tokens(self, min_wallets: int = 2) -> List[TokenInfo]:
        """Retorna tokens presentes em X+ wallets (para UI)"""
        return [
            token for token in self.tokens.values() 
            if len(token.wallets_holding) >= min_wallets
        ]

analyzer = WalletAnalyzer()

# ==================== FUNÇÕES DE ALERTA ====================
async def send_alert(context: ContextTypes.DEFAULT_TYPE, token: TokenInfo):
    if not YOUR_CHAT_ID:
        print(f"⚠️ Alerta: {token.symbol} em {len(token.wallets_holding)} wallets (configure YOUR_CHAT_ID)")
        return
    
    wallets_list = ", ".join(token.wallets_holding)
    total_value = sum(data['value_usd'] for data in token.wallet_data.values())
    
    message = (
        f"🚨 *ALERTA: TOKEN EM COMUM!*\n\n"
        f"🪙 *Token:* {token.symbol}\n"
        f"👛 *Wallets:* {len(token.wallets_holding)} ({wallets_list})\n\n"
    )
    
    message += "*Detalhes:*\n"
    for wallet_name in token.wallets_holding:
        data = token.wallet_data[wallet_name]
        message += f"\n• *{wallet_name}*\n"
        message += f"  💎 {data['amount']:.4f}\n"
        if data['value_usd'] > 0:
            message += f"  💵 ${data['value_usd']:.2f}\n"
    
    if total_value > 0:
        message += f"\n💰 *Total:* ${total_value:.2f}\n"
    
    message += f"\n⏰ {datetime.now().strftime('%d/%m %H:%M:%S')}"
    
    try:
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print(f"✅ Alerta enviado: {token.symbol}")
    except Exception as e:
        print(f"❌ Erro ao enviar alerta: {e}")

async def monitor_wallets(context: ContextTypes.DEFAULT_TYPE):
    print(f"🔍 Monitorando... ({datetime.now().strftime('%H:%M:%S')})")
    
    try:
        await analyzer.analyze_all_wallets()
        new_common = analyzer.get_new_common_tokens(min_wallets=MIN_WALLETS_FOR_ALERT)
        
        if new_common:
            print(f"🎯 {len(new_common)} novo(s) token(s) detectado(s)!")
            for token in new_common:
                await send_alert(context, token)
                analyzer.mark_as_alerted(token.mint)
                await asyncio.sleep(2)
        else:
            print(f"✓ Nenhum novo token ({len(analyzer.tokens)} monitorados)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

# ==================== COMANDOS DO BOT ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    keyboard = [
        [InlineKeyboardButton("📊 Analisar Agora", callback_data='analyze')],
        [InlineKeyboardButton("🎯 Tokens em Comum", callback_data='common')],
        [InlineKeyboardButton("💰 Resumo", callback_data='summary')],
        [InlineKeyboardButton("🔔 Status", callback_data='status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🤖 *Bot de Análise de Wallets*\n\n"
        f"📱 {len(WALLETS)} wallets monitoradas\n"
        f"🔔 Alertas: {'✅ ATIVO' if YOUR_CHAT_ID else '⚠️ Configure'}\n"
        f"⏱️ Verifica a cada {CHECK_INTERVAL_MINUTES} min\n"
        f"🎯 Alerta com {MIN_WALLETS_FOR_ALERT}+ wallets\n\n"
    )
    
    if not YOUR_CHAT_ID:
        message += f"💡 *Seu Chat ID:* `{chat_id}`\n"
        message += "_(Adicione no código)_\n\n"
    
    message += "Escolha uma opção:"
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'analyze':
        await query.edit_message_text("⏳ Analisando...")
        try:
            await analyzer.analyze_all_wallets()
            common = analyzer.get_common_tokens(min_wallets=MIN_WALLETS_FOR_ALERT)
            await query.edit_message_text(
                f"✅ Pronto!\n\n"
                f"🪙 {len(analyzer.tokens)} tokens\n"
                f"🎯 {len(common)} em comum\n"
                f"⏰ {datetime.now().strftime('%H:%M')}",
                parse_mode='Markdown'
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")
    
    elif query.data == 'common':
        await show_common_tokens(query)
    elif query.data == 'summary':
        await show_summary(query)
    elif query.data == 'status':
        await show_status(query)

async def show_common_tokens(query):
    common = analyzer.get_common_tokens(min_wallets=MIN_WALLETS_FOR_ALERT)
    
    if not common:
        await query.edit_message_text(f"❌ Nenhum token em {MIN_WALLETS_FOR_ALERT}+ wallets")
        return
    
    message = f"🎯 *TOKENS EM COMUM*\n\n"
    
    for token in common[:10]:
        wallets = ", ".join(list(token.wallets_holding)[:3])
        total = sum(d['value_usd'] for d in token.wallet_data.values())
        
        message += f"*{token.symbol}*\n"
        message += f"👛 {len(token.wallets_holding)}: {wallets}\n"
        if total > 0:
            message += f"💰 ${total:.2f}\n"
        message += "\n"
    
    await query.edit_message_text(message, parse_mode='Markdown')

async def show_summary(query):
    if not analyzer.tokens:
        await query.edit_message_text("❌ Faça uma análise primeiro!")
        return
    
    common = len(analyzer.get_common_tokens(min_wallets=MIN_WALLETS_FOR_ALERT))
    total_value = sum(sum(d['value_usd'] for d in t.wallet_data.values()) for t in analyzer.tokens.values())
    
    message = (
        f"💰 *RESUMO*\n\n"
        f"👛 {len(WALLETS)} wallets\n"
        f"🪙 {len(analyzer.tokens)} tokens\n"
        f"🎯 {common} em comum\n"
    )
    
    if total_value > 0:
        message += f"💵 ${total_value:.2f}\n"
    
    message += f"\n⏰ {analyzer.last_check.strftime('%H:%M')}"
    
    await query.edit_message_text(message, parse_mode='Markdown')

async def show_status(query):
    message = (
        f"🔔 *STATUS*\n\n"
        f"✅ Rodando\n"
        f"⏱️ A cada {CHECK_INTERVAL_MINUTES} min\n"
        f"🎯 Alerta: {MIN_WALLETS_FOR_ALERT}+ wallets\n"
        f"📊 {len(analyzer.tokens)} tokens\n"
        f"🚨 {len(analyzer.alerted_tokens)} alertados\n"
        f"⏰ {analyzer.last_check.strftime('%H:%M')}\n\n"
    )
    
    if YOUR_CHAT_ID:
        message += "✅ Alertas ativos"
    else:
        message += "⚠️ Configure YOUR_CHAT_ID"
    
    await query.edit_message_text(message, parse_mode='Markdown')

# ==================== MAIN ====================
def main():
    print("🚀 Iniciando bot...")
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Configure TELEGRAM_BOT_TOKEN!")
        return
    
    if not YOUR_CHAT_ID:
        print("⚠️ YOUR_CHAT_ID não configurado")
    
    # Cria aplicação
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print(f"✅ Bot ativo!")
    print(f"🔔 Monitoramento: {CHECK_INTERVAL_MINUTES} min")
    print(f"🎯 Alerta: {MIN_WALLETS_FOR_ALERT}+ wallets")
    
    # Adiciona job de monitoramento
    app.job_queue.run_repeating(
        monitor_wallets,
        interval=CHECK_INTERVAL_MINUTES * 60,
        first=10
    )
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
