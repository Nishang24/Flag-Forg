import requests
import json

api_url = 'http://localhost:9000'

# Add workers
workers = [
    {'name': 'John Smith', 'position': 'Head Chef', 'department': 'Kitchen', 'email': 'john@company.com', 'status': 'Active'},
    {'name': 'Maria Garcia', 'position': 'Quality Supervisor', 'department': 'Quality Control', 'email': 'maria@company.com', 'status': 'Active'},
    {'name': 'Ahmed Hassan', 'position': 'Inventory Manager', 'department': 'Storage', 'email': 'ahmed@company.com', 'status': 'Active'},
    {'name': 'Lisa Wong', 'position': 'Production Lead', 'department': 'Kitchen', 'email': 'lisa@company.com', 'status': 'Active'},
]

print('📝 ADDING WORKERS...')
for w in workers:
    r = requests.post(api_url + '/workers', json=w)
    if r.status_code == 200:
        print('✅ ' + w['name'])

# Add inventory
inventory = [
    {'name': 'Premium Flour', 'category': 'Raw Materials', 'sku': 'FLOUR001', 'quantity': 500, 'unit': 'kg', 'price_per_unit': 2.50},
    {'name': 'Olive Oil', 'category': 'Raw Materials', 'sku': 'OIL001', 'quantity': 100, 'unit': 'liters', 'price_per_unit': 12.00},
    {'name': 'Sea Salt', 'category': 'Raw Materials', 'sku': 'SALT001', 'quantity': 50, 'unit': 'kg', 'price_per_unit': 3.50},
    {'name': 'Sugar', 'category': 'Raw Materials', 'sku': 'SUGAR001', 'quantity': 200, 'unit': 'kg', 'price_per_unit': 1.80},
    {'name': 'Packaging Boxes', 'category': 'Supplies', 'sku': 'BOX001', 'quantity': 5000, 'unit': 'pieces', 'price_per_unit': 0.50},
]

print('\n📦 ADDING INVENTORY...')
for i in inventory:
    r = requests.post(api_url + '/inventory', json=i)
    if r.status_code == 200:
        print('✅ ' + i['name'] + ' (' + str(i['quantity']) + ' ' + i['unit'] + ')')

# Add tasks
tasks = [
    {'title': 'Prepare pastry dough', 'status': 'In Progress', 'priority': 'High', 'task_type': 'production'},
    {'title': 'Quality check batch 001', 'status': 'Todo', 'priority': 'High', 'task_type': 'quality'},
    {'title': 'Clean production line', 'status': 'Todo', 'priority': 'Medium', 'task_type': 'maintenance'},
    {'title': 'Package finished goods', 'status': 'Todo', 'priority': 'Medium', 'task_type': 'production'},
]

print('\n📋 ADDING TASKS...')
for t in tasks:
    r = requests.post(api_url + '/tasks', json=t)
    if r.status_code == 200:
        print('✅ ' + t['title'])

print('\n✨ System Setup Complete!')
print('\n' + '='*60)
print('📊 SYSTEM STATUS')
print('='*60)

workers_list = requests.get(api_url + '/workers').json()
inventory_list = requests.get(api_url + '/inventory').json()
tasks_list = requests.get(api_url + '/tasks').json()
audit_logs = requests.get(api_url + '/audit-logs').json()

print('\n👥 WORKERS: ' + str(len(workers_list)) + ' total')
for w in workers_list[:4]:
    print('   - ' + w['name'] + ' (' + w['position'] + ')')

print('\n📦 INVENTORY: ' + str(len(inventory_list)) + ' items')
total_value = sum([item.get('quantity', 0) * item.get('price_per_unit', 0) for item in inventory_list])
print('   - Total inventory value: $' + str(round(total_value, 2)))

print('\n📋 TASKS: ' + str(len(tasks_list)) + ' tasks')
for t in tasks_list[:4]:
    print('   - ' + t['title'] + ' [' + t['priority'] + ']')

print('\n📊 AUDIT LOG EVENTS: ' + str(len(audit_logs)))
print('\n' + '='*60)
print('✅ SYSTEM FULLY OPERATIONAL!')
print('='*60)
print('\n🌐 Dashboard: http://localhost:3000')
print('📡 API Documentation: http://localhost:9000/docs')
print('🎤 Voice Command: Ready to use')
print('\n💡 Try these voice commands:')
print('   "Add 100 kg flour to inventory"')
print('   "Create a new high priority task"')
print('   "Add worker John in kitchen"')
