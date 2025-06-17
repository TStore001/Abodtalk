"""
وحدة الاتصال بـ API Pocket Option ومحرك التداول
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from src.trading_strategies import TechnicalAnalysis

class PocketOptionAPI:
    """فئة للتعامل مع API Pocket Option"""
    
    def __init__(self):
        self.is_connected = False
        self.balance = 1000.0  # رصيد افتراضي للاختبار
        self.currency_pairs = [
            'EUR/USD', 'EUR/USD OTC', 'EUR/RUB OTC', 'BHD/CNY OTC',
            'USD/JPY', 'GBP/CAD', 'GBP/USD', 'AUD/USD'
        ]
        self.price_data = {}
        self.technical_analyzer = TechnicalAnalysis()
        
    async def connect(self, email: str = None, password: str = None) -> bool:
        """الاتصال بـ API (محاكاة)"""
        try:
            # محاكاة الاتصال
            await asyncio.sleep(1)
            self.is_connected = True
            print("✅ تم الاتصال بـ Pocket Option API بنجاح")
            return True
        except Exception as e:
            print(f"❌ فشل الاتصال بـ API: {e}")
            return False
    
    def generate_mock_prices(self, pair: str, count: int = 100) -> List[float]:
        """توليد أسعار وهمية للاختبار"""
        import random
        
        # أسعار أساسية لكل زوج
        base_prices = {
            'EUR/USD': 1.0850,
            'EUR/USD OTC': 1.0855,
            'EUR/RUB OTC': 95.50,
            'BHD/CNY OTC': 18.75,
            'USD/JPY': 149.80,
            'GBP/CAD': 1.7250,
            'GBP/USD': 1.2650,
            'AUD/USD': 0.6580
        }
        
        base_price = base_prices.get(pair, 1.0000)
        prices = []
        current_price = base_price
        
        for _ in range(count):
            # تغيير عشوائي صغير
            change = random.uniform(-0.002, 0.002)
            current_price *= (1 + change)
            prices.append(round(current_price, 5))
        
        return prices
    
    async def get_candles(self, pair: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        """الحصول على بيانات الشموع"""
        if not self.is_connected:
            await self.connect()
        
        prices = self.generate_mock_prices(pair, count)
        candles = []
        
        for i, price in enumerate(prices):
            candle = {
                'time': int(time.time()) - (count - i) * timeframe,
                'open': price * random.uniform(0.999, 1.001),
                'high': price * random.uniform(1.0005, 1.002),
                'low': price * random.uniform(0.998, 0.9995),
                'close': price,
                'volume': random.randint(100, 1000)
            }
            candles.append(candle)
        
        return candles
    
    async def get_current_price(self, pair: str) -> float:
        """الحصول على السعر الحالي"""
        candles = await self.get_candles(pair, count=1)
        return candles[-1]['close'] if candles else 0.0
    
    async def place_order(self, pair: str, direction: str, amount: float, duration: int = 60) -> Dict:
        """وضع أمر تداول"""
        if not self.is_connected:
            return {'success': False, 'error': 'غير متصل بـ API'}
        
        if amount > self.balance:
            return {'success': False, 'error': 'الرصيد غير كافي'}
        
        order_id = f"ORDER_{int(time.time())}"
        entry_price = await self.get_current_price(pair)
        
        # محاكاة نتيجة التداول
        import random
        win_probability = 0.65  # نسبة فوز 65%
        is_win = random.random() < win_probability
        
        if is_win:
            profit = amount * 0.8  # ربح 80%
            self.balance += profit
            result = 'WIN'
        else:
            self.balance -= amount
            profit = -amount
            result = 'LOSS'
        
        order = {
            'success': True,
            'order_id': order_id,
            'pair': pair,
            'direction': direction,
            'amount': amount,
            'entry_price': entry_price,
            'duration': duration,
            'result': result,
            'profit': profit,
            'new_balance': self.balance,
            'timestamp': datetime.now().isoformat()
        }
        
        return order
    
    async def get_balance(self) -> float:
        """الحصول على الرصيد الحالي"""
        return self.balance

class TradingEngine:
    """محرك التداول الرئيسي"""
    
    def __init__(self):
        self.api = PocketOptionAPI()
        self.analyzer = TechnicalAnalysis()
        self.trade_history = []
        self.notifications = []
        self.is_running = False
        self.min_confidence = 75  # الحد الأدنى للثقة لتنفيذ الصفقة
        self.trade_amount = 10.0  # مبلغ التداول الافتراضي
        
    async def start(self):
        """بدء محرك التداول"""
        if not await self.api.connect():
            return False
        
        self.is_running = True
        print("🚀 تم بدء محرك التداول")
        return True
    
    def stop(self):
        """إيقاف محرك التداول"""
        self.is_running = False
        print("⏹️ تم إيقاف محرك التداول")
    
    async def analyze_market(self) -> Dict:
        """تحليل السوق لجميع أزواج العملات"""
        if not self.is_running:
            return {'error': 'محرك التداول غير مفعل'}
        
        analysis_results = {}
        high_confidence_signals = []
        
        for pair in self.api.currency_pairs:
            try:
                # الحصول على بيانات الأسعار
                candles = await self.api.get_candles(pair, count=100)
                prices = [candle['close'] for candle in candles]
                
                # تحليل الزوج
                analysis = self.analyzer.analyze_pair(pair, prices)
                analysis_results[pair] = analysis
                
                # التحقق من الإشارات عالية الثقة
                consensus = analysis.get('consensus', {})
                if (consensus.get('signal') != 'HOLD' and 
                    consensus.get('confidence', 0) >= self.min_confidence):
                    
                    high_confidence_signals.append({
                        'pair': pair,
                        'signal': consensus['signal'],
                        'confidence': consensus['confidence'],
                        'strength': consensus['strength'],
                        'price': analysis['current_price']
                    })
                
            except Exception as e:
                analysis_results[pair] = {
                    'error': f'خطأ في تحليل {pair}: {str(e)}'
                }
        
        # إضافة إشعارات للإشارات عالية الثقة
        for signal in high_confidence_signals:
            await self.add_notification(
                f"إشارة قوية: {signal['pair']} - {signal['signal']} "
                f"(ثقة: {signal['confidence']:.1f}%)",
                'high_confidence_signal'
            )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis_results,
            'high_confidence_signals': high_confidence_signals,
            'total_pairs': len(self.api.currency_pairs),
            'signals_found': len(high_confidence_signals)
        }
    
    async def execute_trade(self, pair: str, signal: str, confidence: float) -> Dict:
        """تنفيذ صفقة تداول"""
        if not self.is_running:
            return {'success': False, 'error': 'محرك التداول غير مفعل'}
        
        if confidence < self.min_confidence:
            return {'success': False, 'error': f'مستوى الثقة منخفض: {confidence:.1f}%'}
        
        # تنفيذ الصفقة
        result = await self.api.place_order(
            pair=pair,
            direction=signal,
            amount=self.trade_amount
        )
        
        if result.get('success'):
            # إضافة إلى سجل التداول
            trade_record = {
                'id': len(self.trade_history) + 1,
                'timestamp': result['timestamp'],
                'pair': pair,
                'direction': signal,
                'amount': self.trade_amount,
                'entry_price': result['entry_price'],
                'confidence': confidence,
                'result': result['result'],
                'profit': result['profit'],
                'balance': result['new_balance']
            }
            
            self.trade_history.append(trade_record)
            
            # إضافة إشعار
            await self.add_notification(
                f"تم تنفيذ صفقة: {pair} - {signal} - النتيجة: {result['result']} "
                f"(ربح/خسارة: {result['profit']:.2f})",
                'trade_executed'
            )
        
        return result
    
    async def add_notification(self, message: str, type: str = 'info'):
        """إضافة إشعار جديد"""
        notification = {
            'id': len(self.notifications) + 1,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': type,
            'read': False
        }
        
        self.notifications.append(notification)
        
        # الاحتفاظ بآخر 100 إشعار فقط
        if len(self.notifications) > 100:
            self.notifications = self.notifications[-100:]
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """الحصول على سجل التداول"""
        return self.trade_history[-limit:] if self.trade_history else []
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """الحصول على الإشعارات"""
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return self.notifications
    
    def mark_notification_read(self, notification_id: int):
        """تمييز إشعار كمقروء"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات التداول"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'current_balance': self.api.balance
            }
        
        winning_trades = len([t for t in self.trade_history if t['result'] == 'WIN'])
        losing_trades = len([t for t in self.trade_history if t['result'] == 'LOSS'])
        total_profit = sum([t['profit'] for t in self.trade_history])
        
        return {
            'total_trades': len(self.trade_history),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / len(self.trade_history)) * 100,
            'total_profit': total_profit,
            'current_balance': self.api.balance
        }

