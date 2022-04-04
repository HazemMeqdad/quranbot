import hikari
import lightbulb

interactions = lightbulb.Plugin("interactions")

async def interaction_create_event(event: hikari.InteractionCreateEvent):
    if event.interaction.type == hikari.InteractionType.MESSAGE_COMPONENT and event.interaction.custom_id == "add_role":
        # user = interactions.bot.cache.get_member(event.interaction.member.guild_id, event.interaction.member.user)
        # if not user:
        user = await event.app.rest.fetch_member(event.interaction.member.guild_id, event.interaction.member.user)
        role_ids = user.role_ids
        if 960519125082464287 in role_ids:
            await event.app.rest.remove_role_from_member(event.interaction.member.guild_id, user, 960519125082464287)
            await event.app.rest.create_interaction_response(
                interaction=event.interaction,
                token=event.interaction.token,
                response_type=hikari.ResponseType.MESSAGE_CREATE,
                content="تم الغاء أشتراك بالرتبه بنجاح",
                flags=hikari.MessageFlag.EPHEMERAL
            )
        else:
            await event.app.rest.add_role_to_member(event.interaction.member.guild_id, user, 960519125082464287)
            await event.app.rest.create_interaction_response(
                interaction=event.interaction,
                token=event.interaction.token,
                response_type=hikari.ResponseType.MESSAGE_CREATE,
                content="تم أشتراكك بالرتبه بنجاح",
                flags=hikari.MessageFlag.EPHEMERAL
            )

def load(bot: lightbulb.BotApp):
    bot.add_plugin(interactions)
    bot.event_manager.subscribe(hikari.InteractionCreateEvent, interaction_create_event)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(interactions)
    bot.event_manager.unsubscribe(hikari.InteractionCreateEvent, interaction_create_event)
