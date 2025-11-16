import json
import os

def handler(event, context):
    try:
        # Для теста - просто возвращаем успешный ответ
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Bot is working!',
                'method': event.get('httpMethod', 'GET'),
                'path': event.get('path', '/')
            })
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps({'error': str(e)})
        }
