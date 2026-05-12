from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from core import db
from core.models import User, TestResult

api = Blueprint('api', __name__)

@api.route('/save_result', methods=['POST'])
@login_required
def save_result():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Нет данных'}), 400

    try:
        avg_reaction_time = float(data.get('average_reaction_time'))
        min_reaction_time = float(data.get('min_reaction_time', 0))
        max_reaction_time = float(data.get('max_reaction_time', 0))
        correct_responses = int(data.get('correct_responses', 0))
        total_attempts = int(data.get('total_attempts', 0))
        false_responses = int(data.get('false_responses', 0))

        if avg_reaction_time < 0 or min_reaction_time < 0 or max_reaction_time < 0 or correct_responses < 0 or total_attempts <= 0 or false_responses < 0:
            return jsonify({'success': False, 'message': 'Некорректные данные'}), 400

        # Получаем предыдущий результат для сравнения
        previous_result = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.timestamp.desc()).first()
        previous_avg_comparison = None
        if previous_result:
            previous_avg_comparison = avg_reaction_time - previous_result.average_reaction_time

        result = TestResult(
            user_id=current_user.id,
            average_reaction_time=avg_reaction_time,
            min_reaction_time=min_reaction_time,
            max_reaction_time=max_reaction_time,
            correct_responses=correct_responses,
            total_attempts=total_attempts,
            false_responses=false_responses,
            previous_avg_comparison=previous_avg_comparison
        )
        db.session.add(result)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Результат сохранен', 'result_id': result.id}), 200

        return jsonify({'success': True, 'message': 'Результат сохранен'}), 200

    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'message': 'Ошибка обработки данных'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Ошибка сервера'}), 500

@api.route('/user_stats', methods=['GET'])
@login_required
def get_user_stats():
    user_results = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.timestamp.desc()).all()
    stats = [{
        'id': r.id,
        'timestamp': r.timestamp.isoformat(),
        'average_reaction_time': r.average_reaction_time,
        'correct_responses': r.correct_responses,
        'total_attempts': r.total_attempts
    } for r in user_results]

    return jsonify({'success': True, 'stats': stats})

@api.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    top_results = db.session.query(
        User.username,
        db.func.avg(TestResult.average_reaction_time).label('avg_reaction_time'),
        db.func.count(TestResult.id).label('test_count')
    ).join(TestResult).group_by(User.id).order_by('avg_reaction_time').limit(10).all()

    leaderboard = [{
        'username': result.username,
        'avg_reaction_time': round(result.avg_reaction_time, 2),
        'test_count': result.test_count
    } for result in top_results]

    return jsonify({'success': True, 'leaderboard': leaderboard})