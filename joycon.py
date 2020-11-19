from pyjoycon import JoyCon, get_R_id

joycon_id = get_R_id()
#print(joycon_id)
joycon = JoyCon(*joycon_id)

while(1):
	arr = joycon.get_status()
	print(arr['analog-sticks']['right'])
	#print(arr['buttons']['shared'])
	#print(arr['analog-sticks']['right'])