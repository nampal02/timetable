import discord
import asyncio
import os
from discord.http import Route

app = discord.Client()
http = app.http

dictionary = {}

member_list = ["초기화", "현우", "태현", "영준", "상진"]

team_list = [
["아브", "워로드", "창술사", "데헌", "바드"],
["아브", "스카", "배마", "건슬", "홀나"],
["아브", "바드", "스카", "리퍼", "소서"],
["쿠크", "스카", "창술", "리퍼", "바드"],
["쿠크", "워로드", "스카", "건슬", "홀나"],
["쿠크", "바드", "배마", "데헌", "건슬"],
["비아", "X", "블레", "X", "호크"],
["비아", "X", "X", "X", "건슬"],
["발탄", "워로드", "인파", "데헌", "바드"],
["발탄", "바드", "창술사", "리퍼", "호크"],
["발탄", "스카", "블레", "건슬", "홀나"],
["발탄", "X", "스카", "X", "소서"],
["발탄", "X", "배마", "X", "건슬"],
["비노", "X", "인파", "X", "블래"],
["알고", "스카", "창술", "리퍼", "바드"],
["알고", "워로드", "배마", "건슬", "홀나"],
["알고", "바드", "스카", "데헌", "소서"],
["알고", "X", "블레", "X", "호크"],
["알고", "X", "인파", "X", "건슬"],
["도가토1", "워로드", "창술사", "데헌", "바드"],
["도비스", "워로드", "창술사", "데헌", "바드"],
]

def build_onelist(index):
	built_component = []
	first_row_component = []
	for member in member_list:
		customId = member
		first_row_component.append({"type": 2, "label": member, "style": 2, "custom_id": customId})
	built_component.append({"type":1, "components": first_row_component})

	current = index
	for team in team_list[index:]:
		member_components = []

		region_name = team[0]
		z = 0
		for member in team:
			customId = str(current) + " " + region_name + " " + member_list[z] + " " + member
			if z == 0:
				customId = current
			z = z + 1
			member_components.append({"type": 2, "label": member, "style": 2, "custom_id": customId})
		built_component.append({"type": 1, "components": member_components})

		current = current + 1
	
		offset = current - index
		if offset == 4:
			overflow = True
			return built_component, current, overflow

	overflow = False
	return built_component, current, overflow

@app.event
async def on_ready():
	print("일정 관리 봇 시작합니다.")

	await app.change_presence(status=discord.Status.online, activity=discord.Game("일정 관리 중"))
	
@app.event
async def on_message(message):
	content = message.content
	guild = message.guild
	author = message.author
	channel = message.channel

	if content.startswith("!상태창생성"):
		splited = content.split()
		"""built_component = []
		first_row_component = []
		for member in member_list:
			customId = member
			first_row_component.append({"type": 2, "label": member, "style": 2, "custom_id": customId})

		built_component.append({"type":1, "components": first_row_component})

		team_index = 0
		for team in team_list:
			member_components = []

			z = 0
			for member in team:
				customId = str(team_index) +" "+ splited[2] + " " + member_list[z] + " " + member
				if z == 0:
					customId = team_index
				z = z + 1
				member_components.append({"type": 2, "label": member, "style": 2, "custom_id": customId})
			built_component.append({"type": 1, "components": member_components})

			team_index = team_index + 1"""
		r = Route('POST', '/channels/{channel_id}/messages', channel_id=channel.id)

		next_current = 0
		page_num = 1
		while True:
			built_component, next_current, overflow = build_onelist(next_current)
			title_concat = splited[1] + str(page_num)
			page_num = page_num + 1
			embed = discord.Embed(title=title_concat)
			payload = {
				"embed": embed.to_dict(),
				"components": built_component
			}
			if len(built_component) != 1:
				await http.request(r, json=payload)

			if overflow == False:
				break
		return

@app.event
async def on_socket_response(payload):
	if payload.get("t", "") == "INTERACTION_CREATE" and payload.get("d",{}).get("type") == 3:
		d = payload.get("d", {})
		message = d.get("message", {})

		message_id=message.get('id')
		custom_id = d.get("data", {}).get("custom_id")

		splited_custom_id = custom_id.split()
		if len(splited_custom_id) == 1:
			before_embeds = message["embeds"]
			before_components = message["components"]

			if custom_id == "초기화":

				com_index = 0
				for team_row in before_components:
					member_dic = team_row["components"]

					index2 = 0
					for button in member_dic:
						before_components[com_index]["components"][index2]["style"] = 2
						index2 = index2 + 1
					com_index = com_index + 1
			else:
				team_index = splited_custom_id[0]

				team_index_converted = int(team_index)%4
				team_row = before_components[team_index_converted+1]
				
				member_dic = team_row["components"]
				index2 = 0
				for member in member_dic:
					if member["style"] == 2:
						before_components[team_index_converted+1]["components"][index2]["style"] = 1
					elif member["style"] == 1:
						#print("Style is 1. change")
						before_components[team_index_converted+1]["components"][index2]["style"] = 2

					index2 = index2 + 1

			after_contents = {
				"embeds": before_embeds,
				"components": before_components
			}

			update_route = Route("PATCH", '/channels/{channel_id}/messages/{message_id}', channel_id=message.get("channel_id"), message_id=message.get('id'))
			
			await http.request(update_route, json=after_contents)

			interaction_id = d.get("id")
			interaction_token = d.get("token")

			interaction_route = Route("POST", f"/interactions/{interaction_id}/{interaction_token}/callback")
			await http.request(interaction_route, json={"type": 6})

			return

		elif len(splited_custom_id) == 4:

			team_index = splited_custom_id[0]
			region = splited_custom_id[1]
			human = splited_custom_id[2]
			job = splited_custom_id[3]

			before_embeds = message["embeds"]
			before_components = message["components"]

			if job != 'X':
				team_index_converted = int(team_index)%4
				team_row = before_components[team_index_converted+1]
				member_dic = team_row["components"]
				index2 = 0
				for member in member_dic:
					#print(custom_id)
					#print(member["custom_id"])
					if custom_id == member["custom_id"]:
						#print("Custom Id checked")
						if member["style"] == 2:
							#print("Style is 2. change")
							before_components[team_index_converted+1]["components"][index2]["style"] = 1
							member["style"] = 1
						elif member["style"] == 1:
							#print("Style is 1. change")
							before_components[team_index_converted+1]["components"][index2]["style"] = 2
							member["style"] = 2
					index2 = index2 + 1

			after_contents = {
				"embeds": before_embeds,
				"components": before_components
			}

			#print(after_contents)

			update_route = Route("PATCH", '/channels/{channel_id}/messages/{message_id}', channel_id=message.get("channel_id"), message_id=message.get('id'))
		
			await http.request(update_route, json=after_contents)

			interaction_id = d.get("id")
			interaction_token = d.get("token")

			interaction_route = Route("POST", f"/interactions/{interaction_id}/{interaction_token}/callback")
			await http.request(interaction_route, json={"type": 6})

			return

#token = open("token.txt", "r").readline().split("=")[1]

app.run(os.environ['token'])