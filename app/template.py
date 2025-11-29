import flet as ft
import gemini
import datetime
from exceptions import ModelGenerationError

import time

class Template(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True
        # View
        self.title = ft.Text(
            value= 'Type prompet',
            color= 'white',
            size= 20,
            weight= ft.FontWeight.BOLD,
        )
        self.txt_box = ft.TextField(
            hint_text= 'O que você gostaria de estudar?',
            bgcolor= "black",
            on_submit= self._on_sub,
        )
        self.subtitle = ft.Text(
            value= 'Answer: ',
            color= 'white',
            size= 20,
            weight= ft.FontWeight.BOLD,
        )
        self.send_btn = ft.CupertinoButton(
            disabled= False,
            bgcolor= "blue",
            width=self.page.width * 0.10,
            alignment=ft.alignment.center,
            content= ft.Text(
                'GEN',
                size=18,
                color="white",
            ),
            on_click= self._on_sub,
        )
        # Output items
        self.start_txt = self.__step_view(' Generating...')
        self.step_1 =self.__step_view('     1. Definição do tempo livre.')
        self.step_2 =self.__step_view('     2. Criação dos módulos de estudo.')
        self.step_3 =self.__step_view('     3. Definição das prioridades das tarefas. ')
        self.step_4 =self.__step_view('     4. Aplicação de métodos de estudo científicos ')
        self.end_txt = ft.Text(
            visible= False,
            color= 'green',
            size=16,
        )
        # Output box
        self.output_view = ft.Container(
            width= self.page.width,
            expand= True,
            content= ft.Column(
                controls=[
                    self.start_txt,
                    ft.Container(
                        content= ft.Column(
                            controls=[
                                self.step_1,
                                self.step_2,
                                self.step_3,
                                self.step_4,
                            ],
                            spacing=5,
                        ),
                        margin= ft.margin.only(left= 10),
                    ),
                    self.end_txt,
                ],
                spacing=20,
            ),
        )
        # Template
        self.content = ft.Column(
            controls= [
                ft.Container(
                    padding= ft.padding.only(top=12, bottom=12),
                    content= self.title,
                ),
                
                self.txt_box,

                ft.Container(
                    padding= ft.padding.only(top=12, bottom=12),
                    content= self.subtitle,
                ),

                self.output_view,

                ft.Container(
                    content= self.send_btn,
                    width= self.page.width,
                    alignment= ft.alignment.center_right,
                ),
            ],
            expand= True,
            spacing= 0,
        )
    
    def gen_AI(self, theme):
        msg = 'Standard message!'

        # Start
        time.sleep(2)
        self._on_step_new(step_view= self.start_txt, state=True, enabled=True)

        try: 
            # 1.
            hours_schema = self.freetime_definition()
            # 2.
            modules_schema = self.create_study_modules(theme, hours_schema)
            # 3.
            priorities_schema = self.priorities_definition(modules_schema)
            # 4.
            self.methods_apply(hours_schema, modules_schema, priorities_schema)

            # Success Output
            self.end_txt.color = 'green'
            msg = f' Um plano de estudos para {theme} foi criado, atulize GurSchedule App para ver!'
        except ModelGenerationError as e:
            # Error Output
            self.end_txt.color = 'red'
            msg = str(e)
        except Exception as e:
            # Error Output
            self.end_txt.color = 'red'
            msg = 'Error: The model failed to generate a study plan!'

        # Output
        self.end_txt.value = msg
        # End
        self.end_txt.visible = True
        self.send_btn.content.value = 'RESET'
        self.send_btn.on_click = self.__reset
        self. end_txt.update()
        return
    
    def freetime_definition(self):
        step = self.step_1

        try:
            self._on_step_new(step_view= step, state= True, load= True)

            # Call API method
            date = datetime.date.today()
            hours_schema = gemini.time_definition(date.strftime("%Y-%m-%d"))
            
            self._on_step_new(step_view= step, state= True, success= True)
            return hours_schema
        except Exception as e:
            self._on_step_new(step_view= step, state= True, fail= True)
            raise e
        
    def create_study_modules(self, theme, hours_schema):
        step = self.step_2

        try:
            self._on_step_new(step_view= step, state= True, load= True)

            # Call API method
            total_free_time = hours_schema['totaltime'] if hours_schema else None
            modules_schema = gemini.modules_definition(theme, total_free_time)

            self._on_step_new(step_view= step, state= True, success= True)
            return modules_schema
        except Exception as e:
            self._on_step_new(step_view= step, state= True, fail= True)
            raise e
        
    def priorities_definition(self, modules_schema):
        step = self.step_3

        try:
            self._on_step_new(step_view= step, state= True, load= True)
            
            # Call API method
            priorities_schema = gemini.priorities_definition(f'{modules_schema}')

            self._on_step_new(step_view= step, state= True, success= True)
            return priorities_schema
        except Exception as e:
            self._on_step_new(step_view= step, state= True, fail= True)
            raise e

    def methods_apply(self, hours_schema, modules_schema, priorities_schema):
        step = self.step_4

        try:
            self._on_step_new(step_view= step, state= True, load= True)
            
            # Call API method
            rel_priorities_schema = gemini.priorities_relationships(priorities_schema, modules_schema)
            gemini.methods_apply(hours_schema, rel_priorities_schema)

            self._on_step_new(step_view= step, state= True, success= True)
            return rel_priorities_schema
        except Exception as e:
            self._on_step_new(step_view= step, state= True, fail= True)
            raise e
    
    def _on_sub(self, e):
        self.send_btn.disabled = True
        self.send_btn.update()

        if self.txt_box.value:
            self.gen_AI(self.txt_box.value)

        self.send_btn.disabled = False
        self.send_btn.update()
        pass

    def _on_step_new(self, step_view, state=False, success=False, fail=False, load=False, enabled=False, disabled=False):
        if success: step_view.data['success'](state)
        if fail: step_view.data['fail'](state)
        if load: step_view.data['load'](state)
        if enabled: step_view.data['enabled'](state)
        if disabled: step_view.data['disabled'](state)

    def _out_step(self, step, state):
        event = step.data['disabled']
        return event(state)

    def __reset(self, e):
        self.send_btn.content.value = 'GEN'
        self.txt_box.value = None
        self.end_txt.visible = False

        self._out_step(self.start_txt, True)
        self._out_step(self.step_1, True)
        self._out_step(self.step_2, True)
        self._out_step(self.step_3, True)
        self._out_step(self.step_4, True)

        self.send_btn.on_click = self._on_sub
        self.txt_box.update()
        self.send_btn.update()
        self.end_txt.update()
        pass

    def __step_view(self, msg):
        def __enabled_icon_all(state, success=False, fail=False, load=False):
            if state:
                success_icon.visible = success
                fail_icon.visible = fail
                load_icon.visible = load
                
                success_icon.update()
                fail_icon.update()
                load_icon.update()
                return
            success_icon.visible = success
            fail_icon.visible = fail
            load_icon.visible = load
            return
        def disabled(state):
            if state: 
                text.color = '#80ffffff'
                __enabled_icon_all(state)
                return text.update()
            __enabled_icon_all(state)
            text.color = '#80ffffff'
            return
        def enabled(state):
            if state: 
                text.color = '#ffffff'
                __enabled_icon_all(state)
                return text.update()
            __enabled_icon_all(state)
            text.color = '#ffffff'
            return
        def success(state):
            if state:
                text.color = '#ffffff'
                text.update()
                return __enabled_icon_all(state, success=True)
            __enabled_icon_all(state, success=True)
            text.color = '#ffffff'
            return
        def fail(state):
            if state:
                text.color = '#ffffff'
                text.update()
                return __enabled_icon_all(state, fail=True)
            __enabled_icon_all(state, fail=True)
            text.color = '#ffffff'
            return
        def load(state):
            if state:
                text.color = '#80ffffff'
                text.update()
                return __enabled_icon_all(state, load=True)
            __enabled_icon_all(state, load=True)
            text.color = '#80ffffff'
            return
        
        success_icon = ft.Icon(name=ft.Icons.CHECK, color='green', visible=False)
        fail_icon = ft.Icon(name=ft.Icons.CLOSE, color='red', visible=False)
        load_icon = ft.CupertinoActivityIndicator(radius=15, visible=False)

        text = ft.Text(
            value=msg,
            color='#80ffffff',
            size=16,
        )
        
        row = ft.Row(
            spacing=10,
        
            controls=[
                text,
                success_icon,
                fail_icon,
                load_icon,
            ],
            data={
                'disabled': disabled,
                'enabled': enabled,
                'success': success,
                'fail': fail,
                'load': load
            }
        )
        return row