"""
وحدة استراتيجيات التحليل الفني لبوت Pocket Option
تحتوي على 5 استراتيجيات قوية للتحليل الفني
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

class TechnicalAnalysis:
    """فئة التحليل الفني مع 5 استراتيجيات قوية"""
    
    def __init__(self):
        self.strategies = {
            'trend_following': 'تتبع الاتجاه',
            'range_trading': 'تداول النطاق',
            'breakout': 'الاختراق',
            'swing_trading': 'التداول المتأرجح',
            'scalping': 'المضاربة السريعة'
        }
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """حساب المتوسط المتحرك البسيط"""
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """حساب المتوسط المتحرك الأسي"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """حساب مؤشر القوة النسبية RSI"""
        if len(prices) < period + 1:
            return 50
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """حساب نطاقات بولينجر"""
        if len(prices) < period:
            return 0, 0, 0
        
        sma = self.calculate_sma(prices, period)
        variance = sum([(price - sma) ** 2 for price in prices[-period:]]) / period
        std = variance ** 0.5
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """حساب مؤشر MACD"""
        if len(prices) < slow:
            return 0, 0, 0
        
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        # تبسيط حساب إشارة MACD
        signal_line = macd_line * 0.8  # تقريب مبسط
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def strategy_trend_following(self, prices: List[float]) -> Dict:
        """استراتيجية تتبع الاتجاه"""
        if len(prices) < 50:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'بيانات غير كافية'}
        
        sma_20 = self.calculate_sma(prices, 20)
        sma_50 = self.calculate_sma(prices, 50)
        current_price = prices[-1]
        
        # تحديد الاتجاه
        if sma_20 > sma_50 and current_price > sma_20:
            signal = 'CALL'
            confidence = min(95, 70 + abs(current_price - sma_20) / sma_20 * 100)
            reason = f'اتجاه صاعد قوي - السعر فوق المتوسطات المتحركة'
        elif sma_20 < sma_50 and current_price < sma_20:
            signal = 'PUT'
            confidence = min(95, 70 + abs(current_price - sma_20) / sma_20 * 100)
            reason = f'اتجاه هابط قوي - السعر تحت المتوسطات المتحركة'
        else:
            signal = 'HOLD'
            confidence = 30
            reason = 'اتجاه غير واضح'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'sma_20': sma_20,
            'sma_50': sma_50
        }
    
    def strategy_range_trading(self, prices: List[float]) -> Dict:
        """استراتيجية تداول النطاق"""
        if len(prices) < 20:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'بيانات غير كافية'}
        
        upper_band, middle_band, lower_band = self.calculate_bollinger_bands(prices)
        current_price = prices[-1]
        
        # تحديد موقع السعر في النطاق
        if current_price <= lower_band:
            signal = 'CALL'
            confidence = 85
            reason = f'السعر عند الحد السفلي للنطاق - فرصة شراء'
        elif current_price >= upper_band:
            signal = 'PUT'
            confidence = 85
            reason = f'السعر عند الحد العلوي للنطاق - فرصة بيع'
        else:
            signal = 'HOLD'
            confidence = 40
            reason = 'السعر في منتصف النطاق'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
    
    def strategy_breakout(self, prices: List[float]) -> Dict:
        """استراتيجية الاختراق"""
        if len(prices) < 20:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'بيانات غير كافية'}
        
        # حساب أعلى وأقل سعر في آخر 20 شمعة
        recent_prices = prices[-20:]
        resistance = max(recent_prices)
        support = min(recent_prices)
        current_price = prices[-1]
        
        # تحديد الاختراق
        if current_price > resistance * 1.001:  # اختراق المقاومة
            signal = 'CALL'
            confidence = 90
            reason = f'اختراق المقاومة عند {resistance:.5f}'
        elif current_price < support * 0.999:  # اختراق الدعم
            signal = 'PUT'
            confidence = 90
            reason = f'اختراق الدعم عند {support:.5f}'
        else:
            signal = 'HOLD'
            confidence = 35
            reason = 'لا يوجد اختراق واضح'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'resistance': resistance,
            'support': support
        }
    
    def strategy_swing_trading(self, prices: List[float]) -> Dict:
        """استراتيجية التداول المتأرجح"""
        if len(prices) < 26:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'بيانات غير كافية'}
        
        rsi = self.calculate_rsi(prices)
        macd_line, signal_line, histogram = self.calculate_macd(prices)
        
        # تحديد إشارات التداول المتأرجح
        if rsi < 30 and macd_line > signal_line:
            signal = 'CALL'
            confidence = 80
            reason = f'RSI في منطقة التشبع البيعي ({rsi:.1f}) مع إشارة MACD إيجابية'
        elif rsi > 70 and macd_line < signal_line:
            signal = 'PUT'
            confidence = 80
            reason = f'RSI في منطقة التشبع الشرائي ({rsi:.1f}) مع إشارة MACD سلبية'
        else:
            signal = 'HOLD'
            confidence = 45
            reason = f'RSI: {rsi:.1f} - لا توجد إشارة واضحة'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'rsi': rsi,
            'macd': macd_line
        }
    
    def strategy_scalping(self, prices: List[float]) -> Dict:
        """استراتيجية المضاربة السريعة"""
        if len(prices) < 10:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'بيانات غير كافية'}
        
        # حساب المتوسطات المتحركة السريعة
        ema_5 = self.calculate_ema(prices, 5)
        ema_10 = self.calculate_ema(prices, 10)
        current_price = prices[-1]
        
        # تحديد الزخم قصير المدى
        price_change = (current_price - prices[-2]) / prices[-2] * 100 if len(prices) > 1 else 0
        
        if ema_5 > ema_10 and price_change > 0.01:
            signal = 'CALL'
            confidence = 75
            reason = f'زخم صاعد قصير المدى - تغير السعر: {price_change:.3f}%'
        elif ema_5 < ema_10 and price_change < -0.01:
            signal = 'PUT'
            confidence = 75
            reason = f'زخم هابط قصير المدى - تغير السعر: {price_change:.3f}%'
        else:
            signal = 'HOLD'
            confidence = 50
            reason = 'لا يوجد زخم واضح'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'ema_5': ema_5,
            'ema_10': ema_10,
            'price_change': price_change
        }
    
    def analyze_pair(self, pair: str, prices: List[float]) -> Dict:
        """تحليل شامل لزوج العملات باستخدام جميع الاستراتيجيات"""
        results = {
            'pair': pair,
            'current_price': prices[-1] if prices else 0,
            'strategies': {},
            'consensus': {},
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # تطبيق جميع الاستراتيجيات
        strategies_methods = {
            'trend_following': self.strategy_trend_following,
            'range_trading': self.strategy_range_trading,
            'breakout': self.strategy_breakout,
            'swing_trading': self.strategy_swing_trading,
            'scalping': self.strategy_scalping
        }
        
        signals = []
        confidences = []
        
        for strategy_name, method in strategies_methods.items():
            try:
                result = method(prices)
                results['strategies'][strategy_name] = result
                
                if result['signal'] != 'HOLD':
                    signals.append(result['signal'])
                    confidences.append(result['confidence'])
            except Exception as e:
                results['strategies'][strategy_name] = {
                    'signal': 'ERROR',
                    'confidence': 0,
                    'reason': f'خطأ في التحليل: {str(e)}'
                }
        
        # حساب الإجماع
        if signals:
            call_count = signals.count('CALL')
            put_count = signals.count('PUT')
            avg_confidence = sum(confidences) / len(confidences)
            
            if call_count > put_count:
                consensus_signal = 'CALL'
                consensus_strength = call_count / len(signals) * 100
            elif put_count > call_count:
                consensus_signal = 'PUT'
                consensus_strength = put_count / len(signals) * 100
            else:
                consensus_signal = 'HOLD'
                consensus_strength = 50
            
            results['consensus'] = {
                'signal': consensus_signal,
                'strength': consensus_strength,
                'confidence': avg_confidence,
                'agreeing_strategies': max(call_count, put_count),
                'total_strategies': len(signals)
            }
        else:
            results['consensus'] = {
                'signal': 'HOLD',
                'strength': 0,
                'confidence': 0,
                'agreeing_strategies': 0,
                'total_strategies': 0
            }
        
        return results

