import requests # type: ignore
from datetime import datetime, timedelta

# Replace with your GitLab instance URL and personal access token
GITLAB_URL = 'https://gitlab.example.com'
PRIVATE_TOKEN = 'your_private_token'

def list_all_users():
    headers = {
        'Private-Token': PRIVATE_TOKEN
    }
    params = {
        'per_page': 100  # Set a high value to reduce the number of pages
    }
    users = []
    page = 1

    while True:
        response = requests.get(f'{GITLAB_URL}/api/v4/users', headers=headers, params={**params, 'page': page})
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        users.extend(data)
        page += 1

    return users

def count_users(users):
    now = datetime.now()
    inactive_users = [user for user in users if user['state'] != 'active']
    billable_users = [user for user in users if user['state'] == 'active' and not user['is_admin']]
    
    def filter_by_last_activity(users, days):
        threshold_date = now - timedelta(days=days)
        return [user for user in users if 'last_activity_on' in user and datetime.strptime(user['last_activity_on'], '%Y-%m-%d') < threshold_date]

    billable_no_usage_90_days = filter_by_last_activity(billable_users, 90)
    billable_no_usage_60_days = filter_by_last_activity(billable_users, 60)
    billable_no_usage_30_days = filter_by_last_activity(billable_users, 30)

    return {
        'inactive_users': len(inactive_users),
        'billable_users': len(billable_users),
        'billable_no_usage_90_days': len(billable_no_usage_90_days),
        'billable_no_usage_60_days': len(billable_no_usage_60_days),
        'billable_no_usage_30_days': len(billable_no_usage_30_days)
    }

all_users = list_all_users()
for user in all_users:
    print(user)

user_counts = count_users(all_users)
print(f'Number of contracted licenses: 630')
print(f'Number of billable licenses: {user_counts["billable_users"]}')
print(f'Number of billable users without usage since 90 days: {user_counts["billable_no_usage_90_days"]}')
print(f'Number of billable users without usage since 60 days: {user_counts["billable_no_usage_60_days"]}')
print(f'Number of billable users without usage since 30 days: {user_counts["billable_no_usage_30_days"]}')
print(f'Number of inactive users: {user_counts["inactive_users"]}')
