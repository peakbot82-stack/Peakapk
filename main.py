from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from collections import deque
from datetime import datetime
import requests
import threading
import time
import random
import os
import json
import hashlib
import shutil
import uuid

# ==================== LICENSE MANAGER ====================
class LicenseManager:
    def __init__(self):
        self.license_file = "activation.lic"
        self.id_file = "device_id.txt"
        self.device_id = self.get_or_create_device_id()
        self.validated = False
        self.license_data = None
        
    def get_or_create_device_id(self):
        try:
            if os.path.exists(self.id_file):
                with open(self.id_file, 'r') as f:
                    stored_id = f.read().strip()
                    if stored_id:
                        return stored_id
            
            new_id = self.generate_device_id()
            with open(self.id_file, 'w') as f:
                f.write(new_id)
            return new_id
            
        except Exception as e:
            print(f"Error gestionando ID: {e}")
            return self.generate_device_id()
    
    def generate_device_id(self):
        try:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        except:
            return str(uuid.uuid4())
    
    def validate_license_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                license_data = json.load(f)
                
                expiry_date_str = license_data.get("expiry_date", "")
                if expiry_date_str and expiry_date_str != "9999-12-31":
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                    if datetime.now() > expiry_date:
                        return False, "La licencia ha expirado"
                
                secret = "PREDICTOR_SECRET_2024"
                data_to_hash = f"{license_data['device_id']}{expiry_date_str}{secret}"
                expected_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
                
                if (license_data.get("device_id") == self.device_id and 
                    license_data.get("hash") == expected_hash):
                    self.license_data = license_data
                    return True, "Licencia válida"
                else:
                    return False, "Licencia inválida"
        except Exception as e:
            return False, f"Error validando licencia: {e}"
    
    def save_license(self, src_path):
        try:
            shutil.copy(src_path, self.license_file)
            self.validated = True
            return True
        except Exception as e:
            print(f"Error guardando licencia: {e}")
            return False
    
    def check_activation(self):
        if not os.path.exists(self.license_file):
            return False, "No se encontró archivo de licencia"
            
        try:
            with open(self.license_file, "r") as f:
                license_data = json.load(f)
                
                expiry_date_str = license_data.get("expiry_date", "")
                if expiry_date_str and expiry_date_str != "9999-12-31":
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                    if datetime.now() > expiry_date:
                        return False, "La licencia ha expirado"
                
                secret = "PREDICTOR_SECRET_2024"
                data_to_hash = f"{license_data['device_id']}{expiry_date_str}{secret}"
                expected_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
                
                if (license_data.get("device_id") == self.device_id and 
                    license_data.get("hash") == expected_hash):
                    self.license_data = license_data
                    return True, "Licencia válida"
                else:
                    return False, "Licencia inválida"
        except Exception as e:
            return False, f"Error verificando activación: {e}"
    
    def get_license_info(self):
        if not self.license_data:
            return "No hay información de licencia disponible"
        
        expiry_date = self.license_data.get("expiry_date", "")
        if expiry_date == "9999-12-31":
            expiry_info = "Licencia permanente (nunca expira)"
        else:
            expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
            days_remaining = (expiry_date_obj - datetime.now()).days
            expiry_info = f"Expira: {expiry_date} ({days_remaining} días restantes)"
        
        return (f"ID: {self.license_data.get('device_id', '')[:8]}... | "
                f"Emitida: {self.license_data.get('issue_date', '')} | "
                f"{expiry_info}")

# ==================== COLOR PREDICTOR ====================
class EnhancedColorPredictor:
    def __init__(self):
        self.reset_session()

    def reset_session(self):
        self.session_history = deque(maxlen=20)
        self.last_prediction = None
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.last_pattern_used = None
        self.consecutive_lost_counter = 0
        self.current_strategy = 1

    def set_strategy(self, strategy_number):
        if strategy_number in [1, 2]:
            self.current_strategy = strategy_number

    def process_color(self, new_color: str):
        if new_color not in ['red', 'blue']:
            return
        self.session_history.append(new_color)

    def update_prediction(self, actual_color: str) -> bool:
        was_correct = self.last_prediction == actual_color
        
        if was_correct:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.consecutive_lost_counter = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.consecutive_lost_counter += 1
    
        return was_correct

    def get_prediction(self):
        if not self.session_history:
            return None, 0.0, "Esperando datos..."

        if self.consecutive_lost_counter >= 6:
            normal_prediction, normal_confidence, normal_logic = self._get_normal_prediction()
            forced_prediction = 'blue' if normal_prediction == 'red' else 'red'
            return forced_prediction, 0.85, f"6+ PERDIDAS → Forzando opuesto: {forced_prediction.upper()}"
        
        if self.current_strategy == 1:
            return self._get_strategy_1_prediction()
        else:
            return self._get_strategy_2_prediction()
    
    def _get_normal_prediction(self):
        last_color = self.session_history[-1]
        return last_color, 0.7, f"BASE: Predecir {last_color.upper()}"
    
    def _get_strategy_1_prediction(self):
        last_color = self.session_history[-1]
        final_prediction = last_color
        final_confidence = 0.7
        final_logic = f"ESTRATEGIA #1 BASE: Predecir {last_color.upper()}"
        
        if self.last_pattern_used == "double_repetition":
            if len(self.session_history) < 2 or self.session_history[-2] != self.session_history[-1]:
                self.last_pattern_used = None
                
        if self.last_pattern_used == "triple_repetition":
            if len(self.session_history) < 3 or self.session_history[-3] != self.session_history[-2] or self.session_history[-2] != self.session_history[-1]:
                self.last_pattern_used = None
        
        if len(self.session_history) >= 3:
            if (self.session_history[-3] != self.session_history[-2] and 
                self.session_history[-2] != self.session_history[-1] and 
                self.session_history[-3] == self.session_history[-1]):
                
                final_prediction = 'blue' if last_color == 'red' else 'red'
                final_confidence = 0.85
                final_logic = f"ESTRATEGIA #1 PATRÓN ALTERNO → Predecir {final_prediction.upper()}"
                self.last_pattern_used = "alternation"
                return final_prediction, final_confidence, final_logic
        
        if len(self.session_history) >= 3 and self.last_pattern_used != "triple_repetition":
            if (self.session_history[-3] == self.session_history[-2] and 
                self.session_history[-2] == self.session_history[-1]):
                
                final_prediction = 'blue' if last_color == 'red' else 'red'
                final_confidence = 0.9
                final_logic = f"ESTRATEGIA #1 PATRÓN TRIPLE → Predecir {final_prediction.upper()}"
                self.last_pattern_used = "triple_repetition"
                return final_prediction, final_confidence, final_logic
        
        if len(self.session_history) >= 2 and self.last_pattern_used != "double_repetition" and self.last_pattern_used != "triple_repetition":
            if self.session_history[-2] == self.session_history[-1]:
                final_prediction = 'blue' if last_color == 'red' else 'red'
                final_confidence = 0.8
                final_logic = f"ESTRATEGIA #1 PATRÓN DOBLE → Predecir {final_prediction.upper()}"
                self.last_pattern_used = "double_repetition"
                return final_prediction, final_confidence, final_logic
        
        return final_prediction, final_confidence, final_logic
    
    def _get_strategy_2_prediction(self):
        last_color = self.session_history[-1]
        final_prediction = last_color
        final_confidence = 0.7
        final_logic = f"ESTRATEGIA #2 BASE: Predecir {last_color.upper()}"
        
        if len(self.session_history) >= 3:
            if (self.session_history[-3] != self.session_history[-2] and 
                self.session_history[-2] != self.session_history[-1] and 
                self.session_history[-3] == self.session_history[-1]):
                
                final_prediction = 'blue' if last_color == 'red' else 'red'
                final_confidence = 0.85
                final_logic = f"ESTRATEGIA #2 PATRÓN ALTERNO → Predecir {final_prediction.upper()}"
                self.last_pattern_used = "alternation"
                return final_prediction, final_confidence, final_logic
        
        return final_prediction, final_confidence, final_logic

# ==================== BETTING SYSTEM ====================
class BettingSystem:
    def __init__(self):
        self.base_url = "https://www.ff2016.vip/api"
        self.session = requests.Session()
        self._setup_headers()
        self.token = None
        self.user_id = None
        self.device_id = None
        self.user_data = None
        self.initial_bet = 0.1
        self.current_bet = self.initial_bet
        self.max_consecutive_losses = 5
        self.max_bet = 10.0
        self.consecutive_losses = 0
        self.betting_active = False
        self.balance = 0.0
        
        self.aggressive_sequence = [0.1, 0.3, 0.7, 1.5, 3.2, 6.5, 13, 26.5, 53.5]
    
    def _setup_headers(self):
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Android 10; Mobile)",
            "Accept-Language": "es-ES,es;q=0.9",
            "X-Requested-With": "XMLHttpRequest"
        })
    
    def _generate_device_id(self):
        return ''.join(random.choices('0123456789', k=20))
    
    def login(self, username, password):
        self.device_id = self._generate_device_id()
        url = f"{self.base_url}/user/login?lang=es"
        payload = {
            "account": username,
            "password": password,
            "deviceId": self.device_id
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get("code") == 1:
                self.token = data["data"]["userinfo"]["token"]
                self.user_id = data["data"]["userinfo"]["id"]
                self.session.headers.update({"token": self.token})
                return True, "Login successful"
            else:
                return False, data.get("msg", "Unknown error")
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_account_info(self):
        if not self.token:
            return False, "Please login first"
            
        url = f"{self.base_url}/user/get_user_info?lang=es"
        payload = {"deviceId": self.device_id}
        
        try:
            response = self.session.post(url, json=payload)
            data = response.json()
            
            if data.get("code") == 1:
                self.user_data = data["data"]
                self.balance = float(self.user_data.get("money", 0.0))
                return True, self.user_data
            return False, data.get("msg", "Unknown error")
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def place_bet(self, side, amount):
        if not self.token:
            return False, "Please login first"
            
        url = f"{self.base_url}/game/add_bet?lang=es"
        
        try:
            bet_amount = round(float(amount), 2)
            if bet_amount < 0.1:
                return False, "Minimum bet is 0.10"
        except ValueError:
            return False, "Amount must be a valid number"
            
        payload = {
            "side": side.lower(),
            "money": bet_amount,
            "redeem_id": 0,
            "deviceId": self.device_id
        }
        
        try:
            response = self.session.post(url, json=payload)
            data = response.json()
            
            if data.get("code") == 1:
                self.get_account_info()
                return True, f"Bet placed: {bet_amount} on {side.upper()}"
            else:
                return False, data.get("msg", "Unknown error")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

# ==================== KIVY COLOR WIDGET ====================
class ColorCircle(Widget):
    def __init__(self, color='gray', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(50), dp(50))
        self.color = color
        self.update_color()
    
    def update_color(self, color=None):
        if color:
            self.color = color
        self.canvas.clear()
        with self.canvas:
            if self.color == 'red':
                Color(1, 0, 0, 1)
            elif self.color == 'blue':
                Color(0, 0, 1, 1)
            else:
                Color(0.5, 0.5, 0.5, 1)
            Ellipse(pos=self.pos, size=self.size)
    
    def on_pos(self, *args):
        self.update_color()

# ==================== MAIN APPLICATION ====================
class PredictorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.license_manager = LicenseManager()
        self.predictor = EnhancedColorPredictor()
        self.betting_system = BettingSystem()
        self.api_url = "https://www.ff2016.vip/api/game/getchart?lang=es"
        self.headers = {
            "token": "81c635fe-0f6e-4bff-aede-4a69d9c9ef2d",
            "Content-Type": "application/json"
        }
        self.running = False
        self.last_processed_index = 0
        self.prediction_index = 0
        self.wins = 0
        self.losses = 0
        self.betting_active = False
        self.target_wins = 0
        
        self.auto_betting_settings = {
            'initial_bet': 0.1,
            'max_consecutive_losses': 5,
            'max_bet': 10.0,
            'martingale': False,
            'aggressive': False
        }
    
    def build(self):
        self.title = 'Predictor PRO'
        Window.size = (dp(400), dp(800))
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Título
        title_layout = BoxLayout(size_hint_y=None, height=dp(40))
        title_label = Label(text='PREDICTOR PRO', font_size='20sp', bold=True)
        title_layout.add_widget(title_label)
        main_layout.add_widget(title_layout)
        
        # Información de licencia
        self.license_label = Label(text=self.license_manager.get_license_info(), 
                                   size_hint_y=None, height=dp(30), font_size='10sp')
        main_layout.add_widget(self.license_label)
        
        # Control de sesión y estadísticas
        control_layout = BoxLayout(size_hint_y=None, height=dp(50))
        self.start_btn = Button(text='▶ Iniciar Sesión')
        self.start_btn.bind(on_press=self.toggle_session)
        control_layout.add_widget(self.start_btn)
        
        self.stats_label = Label(text='🏆 0 | ❌ 0')
        control_layout.add_widget(self.stats_label)
        main_layout.add_widget(control_layout)
        
        # Colores
        colors_layout = BoxLayout(size_hint_y=None, height=dp(100))
        
        # Último color
        last_layout = BoxLayout(orientation='vertical')
        last_layout.add_widget(Label(text='Último', font_size='12sp'))
        self.last_color = ColorCircle()
        last_layout.add_widget(self.last_color)
        colors_layout.add_widget(last_layout)
        
        # Predicción
        pred_layout = BoxLayout(orientation='vertical')
        pred_layout.add_widget(Label(text='Predicción', font_size='12sp'))
        self.pred_color = ColorCircle()
        pred_layout.add_widget(self.pred_color)
        colors_layout.add_widget(pred_layout)
        
        # Confianza
        conf_layout = BoxLayout(orientation='vertical')
        conf_layout.add_widget(Label(text='Confianza', font_size='12sp'))
        self.confidence_label = Label(text='0%', font_size='16sp', bold=True)
        conf_layout.add_widget(self.confidence_label)
        colors_layout.add_widget(conf_layout)
        
        main_layout.add_widget(colors_layout)
        
        # Lógica de predicción
        self.logic_label = Label(text='Esperando datos...', 
                                size_hint_y=None, height=dp(30), 
                                font_size='10sp', text_size=(dp(380), None))
        main_layout.add_widget(self.logic_label)
        
        # Login
        login_layout = GridLayout(cols=3, size_hint_y=None, height=dp(120), spacing=dp(5))
        login_layout.add_widget(Label(text='Usuario:', font_size='12sp'))
        self.username_input = TextInput(multiline=False, size_hint_x=1)
        login_layout.add_widget(self.username_input)
        login_layout.add_widget(Label(text=''))
        
        login_layout.add_widget(Label(text='Contraseña:', font_size='12sp'))
        self.password_input = TextInput(password=True, multiline=False)
        login_layout.add_widget(self.password_input)
        
        self.login_btn = Button(text='🔑 Login')
        self.login_btn.bind(on_press=self.login)
        login_layout.add_widget(self.login_btn)
        
        self.balance_label = Label(text='💰 $0.00', font_size='12sp')
        login_layout.add_widget(self.balance_label)
        main_layout.add_widget(login_layout)
        
        # Apuestas manuales
        bet_layout = GridLayout(cols=4, size_hint_y=None, height=dp(50), spacing=dp(5))
        bet_layout.add_widget(Label(text='Monto:', font_size='12sp'))
        self.bet_input = TextInput(text='0.10', multiline=False, input_filter='float')
        bet_layout.add_widget(self.bet_input)
        
        self.bet_red_btn = Button(text='🔴 Rojo')
        self.bet_red_btn.bind(on_press=lambda x: self.place_manual_bet('red'))
        bet_layout.add_widget(self.bet_red_btn)
        
        self.bet_blue_btn = Button(text='🔵 Azul')
        self.bet_blue_btn.bind(on_press=lambda x: self.place_manual_bet('blue'))
        bet_layout.add_widget(self.bet_blue_btn)
        main_layout.add_widget(bet_layout)
        
        # Configuración auto-betting
        auto_config = GridLayout(cols=4, size_hint_y=None, height=dp(80), spacing=dp(3))
        auto_config.add_widget(Label(text='Apuesta inicial:', font_size='10sp'))
        self.initial_bet_input = TextInput(text='0.10', multiline=False, input_filter='float')
        auto_config.add_widget(self.initial_bet_input)
        auto_config.add_widget(Label(text='Máx pérdidas:', font_size='10sp'))
        self.max_losses_input = TextInput(text='5', multiline=False, input_filter='int')
        auto_config.add_widget(self.max_losses_input)
        
        auto_config.add_widget(Label(text='Máx apuesta:', font_size='10sp'))
        self.max_bet_input = TextInput(text='10.0', multiline=False, input_filter='float')
        auto_config.add_widget(self.max_bet_input)
        auto_config.add_widget(Label(text='Objetivo wins:', font_size='10sp'))
        self.target_wins_input = TextInput(text='0', multiline=False, input_filter='int')
        auto_config.add_widget(self.target_wins_input)
        main_layout.add_widget(auto_config)
        
        # Estrategias y auto-betting
        bet_controls = GridLayout(cols=3, size_hint_y=None, height=dp(80), spacing=dp(5))
        
        # Estrategias
        strategy_layout = BoxLayout(orientation='vertical')
        strategy_layout.add_widget(Label(text='Estrategia:', font_size='10sp'))
        strategy_buttons = BoxLayout()
        self.strategy1_btn = ToggleButton(text='#1', group='strategy', state='down')
        self.strategy1_btn.bind(on_press=lambda x: self.change_strategy(1))
        strategy_buttons.add_widget(self.strategy1_btn)
        self.strategy2_btn = ToggleButton(text='#2', group='strategy')
        self.strategy2_btn.bind(on_press=lambda x: self.change_strategy(2))
        strategy_buttons.add_widget(self.strategy2_btn)
        strategy_layout.add_widget(strategy_buttons)
        bet_controls.add_widget(strategy_layout)
        
        # Sistemas de apuesta
        systems_layout = BoxLayout(orientation='vertical')
        systems_layout.add_widget(Label(text='Sistema:', font_size='10sp'))
        systems_buttons = BoxLayout()
        self.martingale_cb = ToggleButton(text='Martingale')
        self.martingale_cb.bind(on_press=self.toggle_martingale)
        systems_buttons.add_widget(self.martingale_cb)
        self.aggressive_cb = ToggleButton(text='Agresiva')
        self.aggressive_cb.bind(on_press=self.toggle_aggressive)
        systems_buttons.add_widget(self.aggressive_cb)
        systems_layout.add_widget(systems_buttons)
        bet_controls.add_widget(systems_layout)
        
        # Auto-betting
        auto_layout = BoxLayout(orientation='vertical')
        auto_layout.add_widget(Label(text='Auto Betting:', font_size='10sp'))
        self.auto_bet_btn = Button(text='⏹ Detenido')
        self.auto_bet_btn.bind(on_press=self.toggle_auto_betting)
        auto_layout.add_widget(self.auto_bet_btn)
        bet_controls.add_widget(auto_layout)
        
        main_layout.add_widget(bet_controls)
        
        # Scroll de logs
        scroll = ScrollView(size_hint_y=1)
        self.log_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        scroll.add_widget(self.log_layout)
        main_layout.add_widget(scroll)
        
        # Verificar licencia
        self.check_license()
        
        # Iniciar polling
        Clock.schedule_interval(self.api_polling, 2)
        
        return main_layout
    
    def check_license(self):
        valid, message = self.license_manager.check_activation()
        if valid:
            self.log('✅ Licencia válida', 'green')
        else:
            self.log(f'❌ {message}', 'red')
            self.show_activation_popup()
    
    def show_activation_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # ID del dispositivo
        content.add_widget(Label(text=f'ID: {self.license_manager.device_id}', 
                                 font_size='12sp', text_size=(dp(300), None)))
        
        # Botón para copiar
        copy_btn = Button(text='📋 Copiar ID', size_hint_y=None, height=dp(40))
        copy_btn.bind(on_press=self.copy_device_id)
        content.add_widget(copy_btn)
        
        # Seleccionar archivo
        file_btn = Button(text='📁 Seleccionar licencia .lic', size_hint_y=None, height=dp(40))
        file_btn.bind(on_press=self.select_license_file)
        content.add_widget(file_btn)
        
        # Info de licencia
        self.license_info_label = Label(text='Selecciona un archivo de licencia', 
                                        font_size='10sp', text_size=(dp(300), None))
        content.add_widget(self.license_info_label)
        
        # Botón activar
        self.activate_btn = Button(text='✅ Activar', size_hint_y=None, height=dp(40))
        self.activate_btn.bind(on_press=self.activate_license)
        content.add_widget(self.activate_btn)
        
        self.activation_popup = Popup(title='Activación Predictor PRO',
                                      content=content,
                                      size_hint=(0.9, 0.7))
        self.activation_popup.open()
    
    def copy_device_id(self, instance):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.license_manager.device_id)
        self.log('📋 ID copiado al portapapeles', 'yellow')
    
    def select_license_file(self, instance):
        from plyer import filechooser
        filechooser.open_file(title='Seleccionar archivo de licencia',
                              filters=[('Archivos .lic', '*.lic')],
                              on_selection=self.on_file_selected)
    
    def on_file_selected(self, selection):
        if selection:
            self.selected_license_file = selection[0]
            self.display_license_info(selection[0])
    
    def display_license_info(self, file_path):
        try:
            with open(file_path, 'r') as f:
                license_data = json.load(f)
                info = f"📄 Archivo: {os.path.basename(file_path)}\n"
                info += f"🆔 ID: {license_data.get('device_id', 'NO ENCONTRADO')[:8]}...\n"
                info += f"📅 Emitida: {license_data.get('issue_date', 'DESCONOCIDA')}\n"
                
                expiry = license_data.get('expiry_date', '')
                if expiry == '9999-12-31':
                    info += "♾️ Permanente (no expira)"
                else:
                    info += f"⏰ Expira: {expiry}"
                
                self.license_info_label.text = info
        except Exception as e:
            self.license_info_label.text = f'❌ Error: {str(e)}'
    
    def activate_license(self, instance):
        if not hasattr(self, 'selected_license_file'):
            self.log('❌ Primero selecciona un archivo de licencia', 'red')
            return
            
        valid, message = self.license_manager.validate_license_file(self.selected_license_file)
        if valid:
            if self.license_manager.save_license(self.selected_license_file):
                self.log('✅ Licencia activada con éxito', 'green')
                self.activation_popup.dismiss()
                self.license_label.text = self.license_manager.get_license_info()
            else:
                self.log('❌ Error guardando licencia', 'red')
        else:
            self.log(f'❌ Licencia inválida: {message}', 'red')
    
    def log(self, message, color='white'):
        label = Label(text=f'[{datetime.now().strftime("%H:%M:%S")}] {message}', 
                      color=self.get_color(color),
                      size_hint_y=None,
                      height=dp(25),
                      font_size='10sp',
                      text_size=(Window.width - dp(20), None))
        label.bind(size=lambda x, y: setattr(x, 'text_size', (x.width, None)))
        self.log_layout.add_widget(label)
        if len(self.log_layout.children) > 100:
            self.log_layout.remove_widget(self.log_layout.children[-1])
    
    def get_color(self, color):
        colors = {
            'green': (0, 1, 0, 1),
            'red': (1, 0, 0, 1),
            'blue': (0, 0, 1, 1),
            'yellow': (1, 1, 0, 1),
            'white': (1, 1, 1, 1)
        }
        return colors.get(color, colors['white'])
    
    def toggle_session(self, instance):
        if not self.running:
            self.predictor = EnhancedColorPredictor()
            self.last_processed_index = 0
            self.prediction_index = 0
            self.wins = 0
            self.losses = 0
            
            # Limpiar logs
            self.log_layout.clear_widgets()
            
            self.running = True
            self.start_btn.text = '⏹ Detener'
            self.log('▶ Sesión iniciada', 'green')
        else:
            self.running = False
            self.start_btn.text = '▶ Iniciar Sesión'
            self.log('⏹ Sesión detenida', 'yellow')
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.log('❌ Ingresa usuario y contraseña', 'red')
            return
            
        success, message = self.betting_system.login(username, password)
        if success:
            self.log(f'✅ Login exitoso: {username}', 'green')
            self.login_btn.text = '✅ Conectado'
            self.login_btn.disabled = True
            self.username_input.disabled = True
            self.password_input.disabled = True
            self.update_balance()
        else:
            self.log(f'❌ Login fallido: {message}', 'red')
    
    def update_balance(self):
        if not self.betting_system.token:
            return
            
        success, result = self.betting_system.get_account_info()
        if success:
            self.betting_system.balance = float(result.get("money", 0.0))
            self.balance_label.text = f'💰 ${self.betting_system.balance:.2f}'
        else:
            self.log(f'❌ Error actualizando balance: {result}', 'red')
        
        if self.running:
            Clock.schedule_once(lambda dt: self.update_balance(), 5)
    
    def place_manual_bet(self, side):
        if not self.betting_system.token:
            self.log('❌ Inicia sesión primero', 'red')
            return
            
        try:
            amount = float(self.bet_input.text)
            if amount < 0.1:
                self.log('❌ Monto mínimo: 0.10', 'red')
                return
        except ValueError:
            self.log('❌ Monto inválido', 'red')
            return
            
        success, message = self.betting_system.place_bet(side, amount)
        if success:
            self.log(f'✅ Apuesta manual: ${amount:.2f} en {side.upper()}', 'blue')
            self.update_balance()
        else:
            self.log(f'❌ Error: {message}', 'red')
    
    def change_strategy(self, strategy):
        self.predictor.set_strategy(strategy)
        self.log(f'🔄 Estrategia cambiada a #{strategy}', 'yellow')
    
    def toggle_martingale(self, instance):
        if instance.state == 'down':
            self.aggressive_cb.state = 'normal'
            self.auto_betting_settings['martingale'] = True
            self.auto_betting_settings['aggressive'] = False
            self.log('🔄 Sistema Martingale activado', 'yellow')
        else:
            self.auto_betting_settings['martingale'] = False
            self.log('🔄 Sistema Martingale desactivado', 'yellow')
    
    def toggle_aggressive(self, instance):
        if instance.state == 'down':
            self.martingale_cb.state = 'normal'
            self.auto_betting_settings['aggressive'] = True
            self.auto_betting_settings['martingale'] = False
            self.log('🔄 Sistema Agresivo activado', 'yellow')
        else:
            self.auto_betting_settings['aggressive'] = False
            self.log('🔄 Sistema Agresivo desactivado', 'yellow')
    
    def update_betting_settings(self):
        try:
            initial_bet = float(self.initial_bet_input.text) if self.initial_bet_input.text else 0.1
            max_losses = int(self.max_losses_input.text) if self.max_losses_input.text else 5
            max_bet = float(self.max_bet_input.text) if self.max_bet_input.text else 10.0
            target_wins = int(self.target_wins_input.text) if self.target_wins_input.text else 0
            
            if initial_bet < 0.1:
                self.log('❌ Apuesta inicial mínima: 0.10', 'red')
                return
                
            self.auto_betting_settings['initial_bet'] = initial_bet
            self.auto_betting_settings['max_consecutive_losses'] = max_losses
            self.auto_betting_settings['max_bet'] = max_bet
            self.target_wins = target_wins
            
            self.betting_system.initial_bet = initial_bet
            self.betting_system.current_bet = initial_bet
            self.betting_system.max_consecutive_losses = max_losses
            self.betting_system.max_bet = max_bet            
            self.log(f'⚙️ Configuración actualizada: ${initial_bet:.2f}, pérdidas máx: {max_losses}, apuesta máx: ${max_bet:.2f}, objetivo: {target_wins} wins', 'blue')
            
        except ValueError:
            self.log('❌ Ingresa valores numéricos válidos', 'red')
    
    def toggle_auto_betting(self, instance):
        if not self.betting_system.token:
            self.log('❌ Inicia sesión primero', 'red')
            return
            
        if not self.running:
            self.log('❌ Inicia la sesión primero', 'red')
            return
            
        if not self.betting_active:
            self.update_betting_settings()
            
            self.betting_system.consecutive_losses = 0
            self.betting_system.current_bet = self.betting_system.initial_bet
            
            self.betting_active = True
            self.auto_bet_btn.text = '▶ Activado'
            self.auto_bet_btn.background_color = (0, 1, 0, 0.5)
            
            strategy = "NINGUNO"
            if self.auto_betting_settings['martingale']:
                strategy = "MARTINGALE"
            elif self.auto_betting_settings['aggressive']:
                strategy = "AGRESIVO"
            
            self.log(f'🤖 Auto-betting iniciado (Estrategia: {strategy})', 'green')
        else:
            self.betting_active = False
            self.auto_bet_btn.text = '⏹ Detenido'
            self.auto_bet_btn.background_color = (1, 1, 1, 0.5)
            self.log('⏹ Auto-betting detenido', 'yellow')
    
    def place_auto_bet(self, prediction):
        if not self.betting_active or not self.betting_system.token:
            return
            
        if self.betting_system.balance < self.betting_system.current_bet:
            self.log(f'❌ Saldo insuficiente: ${self.betting_system.balance:.2f} < ${self.betting_system.current_bet:.2f}', 'red')
            self.toggle_auto_betting(self.auto_bet_btn)
            return
            
        success, message = self.betting_system.place_bet(prediction, self.betting_system.current_bet)
        if success:
            self.log(f'🤖 Apuesta automática: ${self.betting_system.current_bet:.2f} en {prediction.upper()}', 'blue')
            self.update_balance()
        else:
            self.log(f'❌ Error en apuesta automática: {message}', 'red')
    
    def check_target_wins(self):
        if self.target_wins > 0 and self.wins >= self.target_wins:
            self.log(f'🎯 ¡OBJETIVO ALCANZADO! {self.wins} wins', 'green')
            self.toggle_auto_betting(self.auto_bet_btn)
            if self.running:
                self.toggle_session(self.start_btn)
            return True
        return False
    
    def api_polling(self, dt):
        if self.running:
            try:
                response = requests.post(self.api_url, headers=self.headers, timeout=5)
                if response.ok:
                    data = response.json()
                    if data.get('code') == 1:
                        new_colors = data['data']['ori'][self.last_processed_index:]
                        if new_colors:
                            self.last_processed_index += len(new_colors)
                            last_color = new_colors[-1].lower()
                            Clock.schedule_once(lambda dt, c=last_color: self.process_color(c), 0)
            except Exception as e:
                self.log(f'⚠️ Error API: {str(e)}', 'yellow')
    
    def process_color(self, color):
        if not self.running:
            return
            
        self.predictor.process_color(color)
        
        if color in ['red', 'blue']:
            self.last_color.update_color(color)
        
        if self.predictor.last_prediction is not None:
            self.verify_prediction()
        else:
            self.process_round()
    
    def process_round(self):
        if self.predictor.session_history and self.predictor.last_prediction is None:
            pred, conf, logic = self.predictor.get_prediction()
            if pred:
                self.prediction_index += 1
                color = "red" if pred == 'red' else 'blue'
                self.predictor.last_prediction = pred
                self.pred_color.update_color(color)
                self.confidence_label.text = f'{int(conf*100)}%'
                
                strategy_info = f" | Estrategia: #{self.predictor.current_strategy}"
                bet_info = f" | Apuesta: ${self.betting_system.current_bet:.2f}" if self.betting_active else ""
                balance_info = f" | Balance: ${self.betting_system.balance:.2f}" if self.betting_system.token else ""
                self.logic_label.text = f'{logic}{strategy_info}{bet_info}{balance_info}'
                
                self.log(f'🎯 Predicción #{self.prediction_index}: {pred.upper()}{strategy_info}{bet_info}', 'blue')
                
                if self.betting_active:
                    self.place_auto_bet(pred)
    
    def verify_prediction(self):
        actual = self.predictor.session_history[-1] if self.predictor.session_history else None
        if actual in ['red', 'blue']:
            correct = self.predictor.update_prediction(actual)
            result = "✅ CORRECTO" if correct else "❌ INCORRECTO"
            color = "green" if correct else "red"
            
            strategy_info = f" | Estrategia: #{self.predictor.current_strategy}"
            bet_info = f" | Apuesta: ${self.betting_system.current_bet:.2f}" if self.betting_active else ""
            balance_info = f" | Balance: ${self.betting_system.balance:.2f}" if self.betting_system.token else ""
            
            self.log(f'📊 Resultado #{self.prediction_index}: {actual.upper()} → {result}{strategy_info}{bet_info}', color)
            
            if correct:
                self.wins += 1
                if self.check_target_wins():
                    return
                    
                if self.betting_active:
                    self.betting_system.current_bet = self.auto_betting_settings['initial_bet']
                    self.betting_system.consecutive_losses = 0
                    self.log('🔄 Apuesta reiniciada a inicial', 'yellow')
                    
            else:
                self.losses += 1
                if self.betting_active:
                    self.betting_system.consecutive_losses += 1
                    
                    if self.betting_system.consecutive_losses >= self.auto_betting_settings['max_consecutive_losses']:
                        self.log(f'⛔ Stop loss activado! {self.betting_system.consecutive_losses} pérdidas consecutivas', 'red')
                        self.toggle_auto_betting(self.auto_bet_btn)
                        
                    else:
                        if self.auto_betting_settings['martingale']:
                            new_bet = min(self.betting_system.current_bet * 2, self.auto_betting_settings['max_bet'])
                            self.log(f'🔄 Martingale: ${self.betting_system.current_bet:.2f} → ${new_bet:.2f}', 'yellow')
                            self.betting_system.current_bet = new_bet
                            
                        elif self.auto_betting_settings['aggressive']:
                            loss_count = min(self.betting_system.consecutive_losses, len(self.betting_system.aggressive_sequence) - 1)
                            new_bet = min(self.betting_system.aggressive_sequence[loss_count], self.auto_betting_settings['max_bet'])
                            self.log(f'🔄 Agresiva: ${self.betting_system.current_bet:.2f} → ${new_bet:.2f}', 'yellow')
                            self.betting_system.current_bet = new_bet
            
            self.stats_label.text = f'🏆 {self.wins} | ❌ {self.losses}'
            self.predictor.last_prediction = None
            self.process_round()

if __name__ == '__main__':
    PredictorApp().run()
