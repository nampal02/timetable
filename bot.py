import discord
import asyncio
import os
from discord.http import Route

app = discord.Client()
http = app.http

dictionary = {}

member_list = ["군단장", "현우", "태현", "영준", "상진"]

team_list = [
["아브", "워로드", "창술사", "데헌", "바드"],
["아브", "스카", "배마", "건슬", "홀나"],
["아브", "바드", "스카", "리퍼", "소서"],
["쿠크", "스카", "창술", "리퍼", "바드"],
["쿠크", "워로드", "배마", "건슬", "홀나"],
["쿠크", "바드", "스카", "데헌", "소서"],
["비아", "X", "X", "X", "건슬"],
["발탄1", "워로드", "인파", "데헌", "바드"],
["발탄1", "바드", "창술사", "리퍼", "호크"],
["발탄1", "스카", "블레", "건슬", "홀나"],
["발탄1", "X", "스카", "X", "소서"],
["발탄2", "X", "배마", "X", "건슬"],
["알고", "스카", "창술", "건슬", "바드"],
["알고", "워로드", "배마", "리퍼", "홀나"],
["알고", "바드", "스카", "데헌", "소서"]
]

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
		title_concat = splited[1] + " " + splited[2]
		embed = discord.Embed(title=title_concat)
		built_component = []
		first_row_component = []
		for member in member_list:
			customId = member
			first_row_component.append({"type": 2, "label": member, "style": 2, "custom_id": customId})

		built_component.append({"type":1, "components": first_row_component})

		team_index = 0
		for team in team_list:
			member_components = []

			if team[0] != splited[2]:
				continue

			z = 0
			for member in team:
				customId = str(team_index) +" "+ splited[2] + " " + member_list[z] + " " + member
				if z == 0:
					customId = team_index
				z = z + 1
				member_components.append({"type": 2, "label": member, "style": 2, "custom_id": customId})
			built_component.append({"type": 1, "components": member_components})

			team_index = team_index + 1

		r = Route('POST', '/channels/{channel_id}/messages', channel_id=channel.id)
		#print(built_component)
		payload = {
			"embed": embed.to_dict(),
			"components": built_component
		}

		await http.request(r, json=payload)
		return

"""@app.event
async def on_message(message):
	content = message.content
	guild = message.guild
	author = message.author
	channel = message.channel

	if message.author.bot:
		return None
	if content.startswith("!상태창생성"):
		splited = content.split()
		title_spaced = splited[1] + "                                          "
		embed = discord.Embed(title=title_spaced)

		out = []
		for member in member_list:
			out.append("")

		
		for team in team_list:
			i = 0
			for member in team:
				out[i] += "{}\n".format(member)
				i = i +1

		j = 0
		for member in member_list:
			embed.add_field(name=member, value=out[j], inline=True)
			j = j + 1

		await channel.send(embed=embed)
	if content.startswith("!Test"):
		await channel.send(temp)
"""
@app.event
async def on_socket_response(payload):
	if payload.get("t", "") == "INTERACTION_CREATE" and payload.get("d",{}).get("type") == 3:
		d = payload.get("d", {})
		message = d.get("message", {})

		message_id=message.get('id')
		custom_id = d.get("data", {}).get("custom_id")

		splited_custom_id = custom_id.split()
		team_index = splited_custom_id[0]
		region = splited_custom_id[1]
		human = splited_custom_id[2]
		job = splited_custom_id[2]

		before_embeds = message["embeds"]
		before_components = message["components"]

		if job != 'X':
			team_row = before_components[int(team_index)+1]
			member_dic = team_row["components"]
			index2 = 0
			for member in member_dic:
				#print(custom_id)
				#print(member["custom_id"])
				if custom_id == member["custom_id"]:
					#print("Custom Id checked")
					if member["style"] == 2:
						#print("Style is 2. change")
						before_components[int(team_index)+1]["components"][index2]["style"] = 1
						member["style"] = 1
					elif member["style"] == 1:
						#print("Style is 1. change")
						before_components[int(team_index)+1]["components"][index2]["style"] = 2
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

#token = open("token.txt", "r").readline()

app.run(os.environ['token'])