from halibot import HalAgent, HalConfigurer, Message
import discord, threading
import asyncio


class DiscordAgent(HalAgent):

	class Configurer(HalConfigurer):
		def configure(self):
			self.optionString('token', prompt='API Token', default='')

	def init(self):
		self.token = self.config.get("token")
		self.client = discord.Client()
		create_client(self.client, self)

		if not self.token:
			self.log.error("token not set, cannot connect to discord")
			self.client.close()
			return

		self.thread = threading.Thread(target=self._run_client)
		self.thread.start()

	def _run_client(self):
		self.client.run(self.token)

	def receive(self, msg):
		asyncio.run_coroutine_threadsafe(self.handle_send(msg), self.client.loop)

	def shutdown(self):
		self.client.close()

	# Received a message from halibot-core, translate to discord-isms
	async def handle_send(self, msg):
		self.log.debug("received target='{}', origin='{}'".format(msg.target, msg.origin))
		target = self.client.get_channel(msg.target.split("/")[-1])
		tmp = await self.client.send_message(target, msg.body)

# Define all the functions in the scope of the discord client
#  We don't want to actually spawn the client until we are actually initializing the agent
#  This should keep the proper module scoping, so there's no weird collisions across multiple agents
def create_client(client, agent):
	@client.event
	async def on_ready():
		pass

	@client.event
	async def on_message(message):
		org = agent.name + "/" + str(message.channel.id)
		msg = Message(body=message.content, author=str(message.author), origin=org)

		agent.dispatch(msg)


