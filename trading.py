"""
نقاط النهاية (API Routes) لبوت Pocket Option
"""

from flask import Blueprint, jsonify, request
from src.pocket_option_api import TradingEngine
import asyncio
import threading
import time

# إنشاء Blueprint
trading_bp = Blueprint('trading', __name__)

# إنشاء محرك التداول العام
trading_engine = TradingEngine()
engine_started = False

def run_async_in_thread(coro):
    """تشغيل دالة async في thread منفصل"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    thread = threading.Thread(target=run)
    thread.start()
    thread.join()

@trading_bp.route('/status', methods=['GET'])
def get_status():
    """الحصول على حالة البوت"""
    global engine_started
    
    return jsonify({
        'status': 'running' if engine_started else 'stopped',
        'connected': trading_engine.api.is_connected,
        'balance': trading_engine.api.balance,
        'pairs_count': len(trading_engine.api.currency_pairs),
        'timestamp': time.time()
    })

@trading_bp.route('/start', methods=['POST'])
def start_trading():
    """بدء محرك التداول"""
    global engine_started
    
    try:
        # تشغيل محرك التداول في thread منفصل
        def start_engine():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(trading_engine.start())
                return result
            finally:
                loop.close()
        
        thread = threading.Thread(target=start_engine)
        thread.start()
        thread.join()
        
        engine_started = True
        
        return jsonify({
            'success': True,
            'message': 'تم بدء محرك التداول بنجاح',
            'status': 'running'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في بدء محرك التداول: {str(e)}'
        }), 500

@trading_bp.route('/stop', methods=['POST'])
def stop_trading():
    """إيقاف محرك التداول"""
    global engine_started
    
    try:
        trading_engine.stop()
        engine_started = False
        
        return jsonify({
            'success': True,
            'message': 'تم إيقاف محرك التداول',
            'status': 'stopped'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في إيقاف محرك التداول: {str(e)}'
        }), 500

@trading_bp.route('/analyze', methods=['GET'])
def analyze_market():
    """تحليل السوق"""
    if not engine_started:
        return jsonify({
            'success': False,
            'error': 'محرك التداول غير مفعل'
        }), 400
    
    try:
        def run_analysis():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(trading_engine.analyze_market())
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_analysis)
        thread.start()
        thread.join()
        
        # الحصول على النتيجة (هذا تبسيط، في التطبيق الحقيقي نحتاج لطريقة أفضل)
        result = asyncio.run(trading_engine.analyze_market())
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في تحليل السوق: {str(e)}'
        }), 500

@trading_bp.route('/trade_history', methods=['GET'])
def get_trade_history():
    """الحصول على سجل التداول"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = trading_engine.get_trade_history(limit)
        
        return jsonify({
            'success': True,
            'data': history,
            'total': len(trading_engine.trade_history)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في الحصول على سجل التداول: {str(e)}'
        }), 500

@trading_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """الحصول على الإشعارات"""
    try:
        unread_only = request.args.get('unread_only', False, type=bool)
        notifications = trading_engine.get_notifications(unread_only)
        
        return jsonify({
            'success': True,
            'data': notifications,
            'total': len(notifications)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في الحصول على الإشعارات: {str(e)}'
        }), 500

@trading_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """تمييز إشعار كمقروء"""
    try:
        trading_engine.mark_notification_read(notification_id)
        
        return jsonify({
            'success': True,
            'message': 'تم تمييز الإشعار كمقروء'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في تمييز الإشعار: {str(e)}'
        }), 500

@trading_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """الحصول على إحصائيات التداول"""
    try:
        stats = trading_engine.get_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في الحصول على الإحصائيات: {str(e)}'
        }), 500

@trading_bp.route('/execute_trade', methods=['POST'])
def execute_trade():
    """تنفيذ صفقة تداول"""
    if not engine_started:
        return jsonify({
            'success': False,
            'error': 'محرك التداول غير مفعل'
        }), 400
    
    try:
        data = request.get_json()
        pair = data.get('pair')
        signal = data.get('signal')
        confidence = data.get('confidence', 0)
        
        if not pair or not signal:
            return jsonify({
                'success': False,
                'error': 'بيانات غير مكتملة'
            }), 400
        
        def run_trade():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    trading_engine.execute_trade(pair, signal, confidence)
                )
            finally:
                loop.close()
        
        result = run_trade()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في تنفيذ الصفقة: {str(e)}'
        }), 500

@trading_bp.route('/pairs', methods=['GET'])
def get_currency_pairs():
    """الحصول على قائمة أزواج العملات"""
    try:
        return jsonify({
            'success': True,
            'data': trading_engine.api.currency_pairs
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'فشل في الحصول على أزواج العملات: {str(e)}'
        }), 500

