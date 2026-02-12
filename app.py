from flask import Flask
import requests, imaplib, email, re, os, threading, time

app = Flask(__name__)

# Variables de entorno
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os
