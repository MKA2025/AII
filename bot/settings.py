import os
import json
import base64
import requests

import bot.helpers.translations as lang

from config import Config
from bot.logger import LOGGER

from .config import Config
from .database.postgres_impl import set_db,users,chats,settings_dict
from .helpers.tidal.tidalapi import tidalapi
from .helpers.utils.common import check_id
from datetime import datetime

class BotSettings:
    def __init__(self):
        # Initialize basic settings
        self.bot_lang = "en"
        self.last_updated = "2025-02-03 04:51:23"  # Updated current time
        self.current_user = "MKA2025"
        
        # Initialize required configs with defaults
        self._init_configs()
        
        # Set core configurations
        self.set_language()
        self.set_db()
        
        # Feature flags with default values
        self.bot_public = True
        self.anti_spam = False
        self.post_art = False
        self.sort_playlist = True
        self.disable_sort_link = False
        self.playlist_conc = False
        self.playlist_zip = True
        self.artist_zip = False
        self.album_zip = True
        self.artist_batch = False
        
        # Load settings from database
        self._load_db_settings()

    def _init_configs(self):
        """Initialize required configs with default values"""
        # Handle API_ID
        try:
            api_id = getattr(Config, 'API_ID', None)
            if not api_id or api_id == '':
                Config.API_ID = 0
            else:
                Config.API_ID = int(str(api_id))
        except (ValueError, TypeError):
            Config.API_ID = 0

        # Handle OWNER_ID
        try:
            owner_id = getattr(Config, 'OWNER_ID', None)
            if not owner_id or owner_id == '':
                Config.OWNER_ID = 0
            else:
                Config.OWNER_ID = int(str(owner_id))
        except (ValueError, TypeError):
            Config.OWNER_ID = 0

        # Set other required configs
        if not hasattr(Config, 'API_HASH') or not Config.API_HASH:
            Config.API_HASH = ""
            
        if not hasattr(Config, 'BOT_TOKEN') or not Config.BOT_TOKEN:
            Config.BOT_TOKEN = ""
            
        if not hasattr(Config, 'DATABASE_URL') or not Config.DATABASE_URL:
            Config.DATABASE_URL = ""

    def _load_db_settings(self):
        """Load settings from database if they exist"""
        if not hasattr(Config, 'DATABASE_URL') or not Config.DATABASE_URL:
            return
            
        try:
            db_settings = settings_dict.find_one({}) or {}
            self.bot_public = db_settings.get('bot_public', self.bot_public)
            self.anti_spam = db_settings.get('anti_spam', self.anti_spam)
            self.post_art = db_settings.get('post_art', self.post_art)
            self.sort_playlist = db_settings.get('sort_playlist', self.sort_playlist)
            self.disable_sort_link = db_settings.get('disable_sort_link', self.disable_sort_link)
            self.playlist_conc = db_settings.get('playlist_conc', self.playlist_conc)
            self.playlist_zip = db_settings.get('playlist_zip', self.playlist_zip)
            self.artist_zip = db_settings.get('artist_zip', self.artist_zip)
            self.album_zip = db_settings.get('album_zip', self.album_zip)
            self.artist_batch = db_settings.get('artist_batch', self.artist_batch)
        except Exception as e:
            print(f"Database Error: {str(e)}")

    def set_language(self):
        """Set the language for the bot"""
        from bot.helpers.translations.tr_en import EN
        self.lang = EN()

    def set_db(self):
        """Initialize database connection if URL exists"""
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            set_db()
            
    def check_shared_username(self,username):
        pass

    def check_auth(self,user_id) -> bool:
        return True

    def check_admin(self,user_id) -> bool:
        try:
            # Default admin check - always return True if OWNER_ID is not set
            if not hasattr(Config, 'OWNER_ID'):
                return True
                
            if check_id(user_id) or str(Config.OWNER_ID) == str(user_id):
                return True
        except:
            # If any error occurs, return True for safety
            return True
        return False

    def toggle_public(self):
        self.bot_public = not self.bot_public
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'bot_public':not self.bot_public},
                {'$set':{'bot_public':self.bot_public}},
                upsert=True
            )

    def toggle_antispam(self):
        self.anti_spam = not self.anti_spam
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'anti_spam':not self.anti_spam},
                {'$set':{'anti_spam':self.anti_spam}},
                upsert=True
            )
        
    def toggle_post_art(self):
        self.post_art = not self.post_art
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'post_art':not self.post_art},
                {'$set':{'post_art':self.post_art}},
                upsert=True
            )

    def toggle_sort_playlist(self):
        self.sort_playlist = not self.sort_playlist
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'sort_playlist':not self.sort_playlist},
                {'$set':{'sort_playlist':self.sort_playlist}},
                upsert=True
            )

    def toggle_disable_sort_link(self):
        self.disable_sort_link = not self.disable_sort_link
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'disable_sort_link':not self.disable_sort_link},
                {'$set':{'disable_sort_link':self.disable_sort_link}},
                upsert=True
            )

    def toggle_playlist_zip(self):
        self.playlist_zip = not self.playlist_zip
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'playlist_zip':not self.playlist_zip},
                {'$set':{'playlist_zip':self.playlist_zip}},
                upsert=True
            )

    def toggle_playlist_conc(self):
        self.playlist_conc = not self.playlist_conc
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'playlist_conc':not self.playlist_conc},
                {'$set':{'playlist_conc':self.playlist_conc}},
                upsert=True
            )

    def toggle_artist_zip(self):
        self.artist_zip = not self.artist_zip
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'artist_zip':not self.artist_zip},
                {'$set':{'artist_zip':self.artist_zip}},
                upsert=True
            )

    def toggle_album_zip(self):
        self.album_zip = not self.album_zip
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'album_zip':not self.album_zip},
                {'$set':{'album_zip':self.album_zip}},
                upsert=True
            )

    def toggle_artist_batch(self):
        self.artist_batch = not self.artist_batch
        if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
            settings_dict.update_one(
                {'artist_batch':not self.artist_batch},
                {'$set':{'artist_batch':self.artist_batch}},
                upsert=True
            )

# Create instance
bot_set = BotSettings()
