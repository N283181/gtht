import json
import os
import random
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Храним данные в памяти (для serverless)
data = {
    'marriages': [],
    'actions': []
}

SEX_ACTIONS = ["выебал", "оттрахал", "занялся сексом с"]
VIOLENCE_ACTIONS = ["ударил", "отпиздил", "избил", "поколотил"]
LOVE_ACTIONS = ["поженился на", "обручился с", "встречается с"]
FRIENDSHIP_ACTIONS = ["подружился с", "запездюлил", "затусил с"]
WEIRD_ACTIONS = ["закопал на даче", "продал в рабство", "украл трусы у"]

class SimpleBot:
    def get_user_name(self, user):
        if user.get('username'):
            return f"@{user['username']}"
        return user.get('first_name', f"User{user['id']}")
    
    def get_marriage(self, user_id):
        for marriage in data['marriages']:
            if (marriage['user1_id'] == user_id or marriage['user2_id'] == user_id) and marriage['is_active']:
                return marriage
        return None
    
    def create_marriage(self, user1, user2):
        if self.get_marriage(user1['id']) or self.get_marriage(user2['id']):
            return False, "❌ Один из пользователей уже в браке!"
        
        marriage = {
            'user1_id': user1['id'], 'user2_id': user2['id'],
            'user1_name': self.get_user_name(user1), 'user2_name': self.get_user_name(user2),
            'married_at': datetime.now().isoformat(), 'is_active': True
        }
        data['marriages'].append(marriage)
        return True, f"💍 {self.get_user_name(user1)} и {self.get_user_name(user2)} теперь муж и жена!"
    
    def divorce(self, user_id):
        marriage = self.get_marriage(user_id)
        if not marriage:
            return False, "❌ Ты не в браке!"
        marriage['is_active'] = False
        return True, f"💔 Брак расторгнут!"
    
    def log_action(self, from_user, to_user, action_type):
        data['actions'].append({
            'from_user_id': from_user['id'], 'to_user_id': to_user['id'],
            'action_type': action_type, 'created_at': datetime.now().isoformat()
        })

def handle_event(event):
    try:
        bot = SimpleBot()
        body = json.loads(event['body'])
        message = body.get('message', {})
        text = message.get('text', '')
        from_user = message.get('from', {})
        chat = message.get('chat', {})
        reply_to = message.get('reply_to_message', {})
        
        if chat.get('type') not in ['group', 'supergroup']:
            return {'statusCode': 200}
        
        if text.startswith('/'):
            command = text.split('@')[0].lower()
            
            if command == '/команды':
                response = "📋 Команды:\n/поженить - создать брак\n/развестись - развод\n/отношения - мои отношения\n/выебать @юзер - секс\n/ударить @юзер - удар"
            
            elif command == '/поженить':
                if reply_to:
                    success, msg = bot.create_marriage(from_user, reply_to['from'])
                    response = msg
                else:
                    response = "❌ Ответь на сообщение!"
            
            elif command == '/развестись':
                success, msg = bot.divorce(from_user['id'])
                response = msg
            
            elif command == '/отношения':
                marriage = bot.get_marriage(from_user['id'])
                response = "💔 Ты одинок" if not marriage else f"💍 В браке с {marriage['user2_name']}"
            
            elif command in ['/выебать', '/ударить']:
                if reply_to:
                    action = random.choice(SEX_ACTIONS if command == '/выебать' else VIOLENCE_ACTIONS)
                    response = f"🔞 {bot.get_user_name(from_user)} {action} {bot.get_user_name(reply_to['from'])}"
                    bot.log_action(from_user, reply_to['from'], 'action')
                else:
                    response = "❌ Ответь на сообщение!"
            
            else:
                response = "❌ Неизвестная команда. /команды"
            
            # Отправляем ответ
            bot_token = os.environ['BOT_TOKEN']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={
                'chat_id': chat['id'],
                'text': response
            })
            
    except Exception as e:
        print(f"Error: {e}")
    
    return {'statusCode': 200}

def lambda_handler(event, context):
    return handle_event(event)
