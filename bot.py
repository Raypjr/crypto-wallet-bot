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
CHECK_INTERVAL_MINUTES = 5  # Verifica a cada 5 minutos
MIN_WALLETS_FOR_ALERT = 2   # Alerta quando 2+ wallets tiverem o mesmo token

# ==================== SUAS WALLETS ====================
WALLETS = {
    "profit": "G5nxEXuFMfV74DSnsrSatqCW32F34XUnBeq3PfDS7w5E",
    "Testiclecabal3": "pJRRw7byDh4witgcYsmGm5N7nEJK1Kzo7U39PkbzQUQ",
    "Andy": "AjmmrnMkd4FHe7HZULcof2WZaR7x2ivdvNJwGcLJz2YS",
    "JizzTrader": "6Ee7NNNNCfbSXKD1u81616Qyj1jK34DyWvvH5BCEsMFU",
    "huigendeshen": "Gdaqp3ND6r3HVAWXpawkQU18EuQqwNxpaeeio8ASVAYd",
    "Psy1": "9hpvgGFPC4dfMEXS6uzjm4xDw41KruviV77FFykbjXXf",
    "Psy2": "49foKJpRnZUaPKsDgnQhUFRMk7NX4zD5KgtVpxgvctLa",
    "Smart2": "BC8yiFFQWFEKrEEj75zYsuK3ZDCfv6QEeMRif9oZZ9TW",
    "Buttwhale": "DPiQs7yP5WnBxN7RwttMKkrndmeTzeVZ69sxeAswxm8r",
    "Asta": "AstaWuJuQiAS3AfqmM3xZxrJhkkZNXtW4VyaGQfqV6JL",
    "Bluechip": "C5tTsPKB9o9Jgqi1SfuwbHY9UHchx5w7VcmCMp5Tmsxu",
    "wechat": "FCkTi9pANbetvGXh73dk6rtSgMz8BoTjRqJMtZ6hxKoV",
    "TesticleCabal3-2": "J2F18fjBTpsX11SCAFF56So8VR57TbALfPHehjxE9gny",
    "UranusSwingTrade": "9bVrnS865n4Rwbkjk5NFzDLBiMifJvMNa7e9HDu6DYSb",
    "Insider": "CyHWA7ru59DRzdZASd7EpJFdn5JfuaSSe1Ges6g3XtLD",
    "TesticleCabal2": "3ffMhPbNhmhzZoUqWNKQ2TKsHSg7UpVJAQzB95Ytrrr6",
    "Uranus0": "8VwmbW9VehM9XEc5tLinSAhag8TcrfcMnagmWKEGtxN7",
    "114514": "C7hiwgERpDEDki8bVHcwADJ1XWjczLw8zRFLtz85cMj5",
    "Wallet-19": "Au1GUWfcadx7jMzhsg6gHGUgViYJrnPfL1vbdqnvLK4i",
    "Teep main 🗿": "5VBaSuVdNCHfNwghyaMKauKZpjXVBJNkLE6yVa8PreQj",
    "Mitch 🤡": "4Be9CvxqHW6BYiRAxW9Q3xu1ycTMWaL5z8NX4HR3ha7t",
    "Him": "DxjmHXm1p7cs8Tezdf2EJm5xnwp9QC2E8CbfD1aXeH1j",
    "Kagami": "DP7G43VPwR5Ab5rcjrCnvJ8UgvRXRHTWscMjRD1eSdGC",
    "noob": "NrnKjCKsPMVyyx6yH7oVL8zFciRiBRuxFjdkSm6DR3x",
    "Powside": "CfExiuWfcCzydS3R4YYEcv8W9NUNgcR9xbApjSiDNr6c",
    "Powmain": "8zFZHuSRuDpuAR7J6FzwyF3vKNx4CVW3DFHJerQhc7Zd",
    "Cards": "3DEmhGgQxHsUXq5vLPc7vaiRP2cdJzU9oGDhpCe7n7b4",
    "0xJumpman": "8eioZubsRjFkNEFcSHKDbWa8MkpmXMBvQcfarGsLviuE",
    "Snowball": "6N4wVaL7hVtNEU9ACQLv9TCeJk8YJMcRhfqe5Vs7Z3F8",
    "Tom": "AWxr21P2srfkPLiPpqDYyWsKWR1bpJWtw5beVMiRxwZm",
    "PnutWhale": "FjmRj8y9xfDaj5Aygq88t5jAFbpxrbZ16JNPPG1sx9FQ",
    "Remus": "BCrTEXmWutwPz8qv6w1S5gDbaLnSLpXKM5kSGVWyyfxu",
    "Gake_Safe": "EwTNPYTuwxMzrvL19nzBsSLXdAoEmVBKkisN87csKgtt",
    "潜水观察员🇨🇳": "C76PFf7f5M6tMPSaTW8ojFiZiY2tmXHifPYsRzo4KzKx",
    "Wallet-35": "AD9suTSgL8rmwmTfb8eWbDg3sqVke1K76jg6Fcf4LubB",
    "Zuna 50%": "E4KuDXd8Y4btRksxrjAXMG1xSwcswtph2ZDGrmd5HMRi",
    "Wallet-37": "H2A4XbExMPHTw4WZP1BbBq1deYgijnAYzdLXSkFxHwrV",
    "王小二": "71CPXu3TvH3iUKaY1bBkAAow24k6tjH473SsKprQBABC",
    "Soloxbt": "FTg1gqW7vPm4kdU1LPM7JJnizbgPdRDy2PitKw6mY27j",
    "Uranus1": "5zbQtt1q8zq1SZY4Doc6ct6PP3DhW8cx5S5z2eTcBaMj",
    "Oxsun 100% (KOL)": "HUpPyLU8KWisCAr3mzWy2FKT6uuxQ2qGgJQxyTpDoes5",
}

# ==================== CLASSES ====================
class TokenInfo:
    def __init__(self, symbol: str, mint: str):
        self.symbol = symbol
        self.mint = mint
        self.wallets_holding: Set[str] = set()
        self.wallet_data: Dict[str, dict] = {}
        self.first_seen = datetime.now()
        
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
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://public-api.solscan.io/token/meta"
                params = {"token": mint_address}
                
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except Exception as e:
                print(f"Erro ao buscar metadata: {e}")
        return {}

class WalletAnalyzer:
    def __init__(self):
        self.rpc_client = PublicRPCClient()
        self.tokens: Dict[str, TokenInfo] = {}
        self.alerted_tokens: Set[str] = set()
        self.last_check = datetime.now()
    
    async def analyze_all_wallets(self) -> Dict[str, TokenInfo]:
        self.tokens.clear()
        
        for wallet_name, wallet_address in WALLETS.items():
            print(f"Analisando {wallet_name}...")
            await self._analyze_wallet(wallet_name, wallet_address)
        
        self.last_check = datetime.now()
        return self.tokens
    
    async def _analyze_wallet(self, wallet_name: str, wallet_address: str):
        token_accounts = await self.rpc_client.get_token_accounts(wallet_address)
        
        for account in token_accounts:
            try:
                parsed = account.get('account', {}).get('data', {}).get('parsed', {})
                info = parsed.get('info', {})
                
                token_mint = info.get('mint')
                amount = float(info.get('tokenAmount', {}).get('uiAmount', 0))
                
                if amount > 0 and token_mint:
                    metadata = await self.rpc_client.get_token_metadata(token_mint)
                    symbol = metadata.get('symbol', 'UNKNOWN')
                    
                    price = await self._get_token_price_jupiter(token_mint)
                    value_usd = amount * price if price else 0
                    
                    if token_mint not in self.tokens:
                        self.tokens[token_mint] = TokenInfo(symbol, token_mint)
                    
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
        common_tokens = [
            token for token in self.tokens.values() 
            if len(token.wallets_holding) >= min_wallets
            and token.mint not in self.alerted_tokens
        ]
        return common_tokens
    
    def mark_as_alerted(self, token_mint: str):
        self.alerted_tokens.add(token_mint)
    
    def get_common_tokens(self, min_wallets: int = 2) -> List[TokenInfo]:
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
async def start_monitoring(application: Application):
    """Inicia o monitoramento periódico"""
    while True:
        await monitor_wallets(application)
        await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)

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
    
    # Inicia monitoramento em background
    asyncio.create_task(start_monitoring(app))
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
