from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from functools import partial
from zai_defs import load, stocks, aggr, ddc, save
load()

arr = []
heads = ["No.", "Style", "Size", "Type", "Quantity", "Price"]

# --- HELPER FUNCTIONS ---

def get_data_list(shop_name):
    if shop_name == 'store': return stocks
    if shop_name == 'Aggrey': return aggr
    if shop_name == 'DDC': return ddc
    return []

# --- CRUD FUNCTIONS ---
# NOTE: Arguments reordered: (screen_obj, shop_name, instance)
# instance is last because Kivy sends it automatically

def add_product(screen_obj, shop_name, instance):
    _layout = GridLayout(cols=2, spacing=dp(10), padding=dp(10))
    
    # Inputs
    _style_ = TextInput(hint_text="Style", multiline=False)
    _size_ = TextInput(hint_text="Size", multiline=False)
    _type_ = TextInput(hint_text="Type", multiline=False)
    _qn_ = TextInput(hint_text="Quantity", multiline=False, input_type='number')
    _price_ = TextInput(hint_text="Price", multiline=False, input_type='number')

    _layout.add_widget(Label(text="[b]Style[/b]", markup=True, color=(0, 1, 0, 1))); _layout.add_widget(_style_)
    _layout.add_widget(Label(text="[b]Size[/b]", markup=True, color=(0, 1, 0, 1))); _layout.add_widget(_size_)
    _layout.add_widget(Label(text="[b]Type[/b]", markup=True, color=(0, 1, 0, 1))); _layout.add_widget(_type_)
    _layout.add_widget(Label(text="[b]Quantity[/b]", markup=True, color=(0, 1, 0, 1))); _layout.add_widget(_qn_)
    _layout.add_widget(Label(text="[b]Price[/b]", markup=True, color=(0, 1, 0, 1))); _layout.add_widget(_price_)

    # Action Buttons
    btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
    btn_add = Button(text="Add", background_color=(0, 1, 0, 1), color=(1, 1, 1, 1))
    btn_close = Button(text="Close", background_color=(1, 0, 0, 1), color=(1, 1, 1, 1))
    
    btn_layout.add_widget(btn_add)
    btn_layout.add_widget(btn_close)
    
    _layout.add_widget(Label()) 
    _layout.add_widget(btn_layout)

    pop1 = Popup(title="Add a product", content=_layout, size_hint=(0.6, 0.6))

    # --- UPDATED LOGIC ---
    def perform_add(btn):
        new_data = [_style_.text, _size_.text, _type_.text, _qn_.text, _price_.text]
        
        # 1. Check if fields are filled
        if all(new_data): 
            target_list = get_data_list(shop_name)
            
            found = False
            
            # 2. Loop through existing items to find a match
            for item in target_list:
                # item is [Style, Size, Type, Qty, Price]
                # We check if Style, Size, and Type match
                if (item[0] == new_data[0] and 
                    item[1] == new_data[1] and 
                    item[2] == new_data[2]):
                    
                    # MATCH FOUND! Update Quantity
                    current_qty = int(item[3])
                    new_qty = int(new_data[3])
                    item[3] = str(current_qty + new_qty)
                    
                    # Optional: Update Price too in case it changed
                    item[4] = new_data[4]
                    
                    found = True
                    break # Stop loop since we found it
            
            # 3. If no match found, Add as new product
            if not found:
                target_list.append(new_data)

            # 4. Save and Refresh
            save() 
            pop1.dismiss()
            screen_obj.refresh_ui()
        else:
            print("Please fill all fields")

    btn_add.bind(on_press=perform_add)
    btn_close.bind(on_press=lambda inst: pop1.dismiss())
    pop1.open()

def remove_product(screen_obj, shop_name, instance):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    input_row = TextInput(hint_text="Enter Row No.", input_type='number', multiline=False)
    content.add_widget(input_row)
    
    btn_confirm = Button(text="Remove", background_color=(1, 0, 0, 1))
    content.add_widget(btn_confirm)

    pop = Popup(title="Remove Product", content=content, size_hint=(0.4, 0.4))

    def do_remove(btn):
        try:
            row = int(input_row.text) - 1 
            target_list = get_data_list(shop_name)
            if 0 <= row < len(target_list):
                del target_list[row]
                save()
                pop.dismiss()
                screen_obj.refresh_ui()
            else:
                print("Invalid row number")
        except ValueError:
            print("Please enter a valid number")

    btn_confirm.bind(on_press=do_remove)
    pop.open()

def edit_product(screen_obj, shop_name, instance):
    # Step 1: Ask for Row Number
    content = BoxLayout(orientation='vertical', padding=dp(10))
    row_input = TextInput(hint_text="Enter Row No. to edit", input_type='number')
    btn_next = Button(text="Next")
    content.add_widget(row_input); content.add_widget(btn_next)

    pop1 = Popup(title="Edit Product - Step 1", content=content, size_hint=(0.4, 0.3))

    def step2(btn):
        try:
            row = int(row_input.text) - 1
            target_list = get_data_list(shop_name)
            if 0 <= row < len(target_list):
                pop1.dismiss()
                open_edit_popup(row, target_list)
            else:
                print("Invalid Row")
        except: pass

    btn_next.bind(on_press=step2)
    pop1.open()

    def open_edit_popup(row, data_list):
        # Step 2: Edit values
        current_data = data_list[row]
        layout = GridLayout(cols=2, padding=dp(10))
        
        inp_style = TextInput(text=current_data[0])
        inp_size = TextInput(text=current_data[1])
        inp_type = TextInput(text=current_data[2])
        inp_qn = TextInput(text=current_data[3])
        inp_price = TextInput(text=current_data[4])

        layout.add_widget(Label(text="Style")); layout.add_widget(inp_style)
        layout.add_widget(Label(text="Size")); layout.add_widget(inp_size)
        layout.add_widget(Label(text="Type")); layout.add_widget(inp_type)
        layout.add_widget(Label(text="Qty")); layout.add_widget(inp_qn)
        layout.add_widget(Label(text="Price")); layout.add_widget(inp_price)
        
        btn_save = Button(text="Save Changes", background_color=(0, 1, 0, 1))
        layout.add_widget(Label()) 
        layout.add_widget(btn_save)

        pop2 = Popup(title="Edit Details", content=layout, size_hint=(0.6, 0.5))

        def save_changes(btn):
            data_list[row] = [inp_style.text, inp_size.text, inp_type.text, inp_qn.text, inp_price.text]
            save()
            pop2.dismiss()
            screen_obj.refresh_ui()

        btn_save.bind(on_press=save_changes)
        pop2.open()

def deliver_product(screen_obj, shop_name, instance):
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    row_input = TextInput(hint_text="Enter Row No.", input_type='number')
    qty_input = TextInput(hint_text="Qty to Deliver", input_type='number')
    btn_go = Button(text="Deliver", background_color=(0, 1, 1, 1))
    
    content.add_widget(row_input)
    content.add_widget(qty_input)
    content.add_widget(btn_go)

    pop = Popup(title="Deliver Stock", content=content, size_hint=(0.4, 0.4))

    def do_deliver(btn):
        try:
            row = int(row_input.text) - 1
            qty_del = int(qty_input.text)
            target_list = get_data_list(shop_name)
            
            if 0 <= row < len(target_list):
                current_qty = int(target_list[row][3])
                if current_qty >= qty_del:
                    new_qty = current_qty - qty_del
                    target_list[row][3] = str(new_qty)
                    save()
                    pop.dismiss()
                    screen_obj.refresh_ui()
                else:
                    print("Not enough stock")
            else:
                print("Invalid Row")
        except:
            print("Error in input")

    btn_go.bind(on_press=do_deliver)
    pop.open()

def filter_product(screen_obj, shop_name, instance):
    content = BoxLayout(orientation='vertical', padding=dp(10))
    search_input = TextInput(hint_text="Enter keyword (Style/Size)")
    btn_search = Button(text="Search")
    
    result_lbl = Label(text="Results will appear here...", size_hint_y=None, height=dp(100))
    
    content.add_widget(search_input)
    content.add_widget(btn_search)
    
    scroll = ScrollView()
    scroll.add_widget(result_lbl)
    content.add_widget(scroll)

    pop = Popup(title="Filter Products", content=content, size_hint=(0.6, 0.6))

    def do_search(btn):
        keyword = search_input.text.lower()
        target_list = get_data_list(shop_name)
        results = []
        
        for idx, item in enumerate(target_list):
            if keyword in str(item).lower():
                results.append(f"Row {idx+1}: {item}")
        
        if results:
            result_lbl.text = "\n".join(results)
        else:
            result_lbl.text = "No matches found."

    btn_search.bind(on_press=do_search)
    pop.open()


# --- GUI GENERATOR ---


def gui(screen_instance, name, array):
    btn_arr = [
            ["Add", add_product],
           ["Edit", edit_product],
           ["Deliver", deliver_product],
           ["Remove", remove_product],
           ["Filter", filter_product]
    ]

    # Helper function to safely switch screens and refresh them
    def switch_and_refresh(target_screen_name):
        screen_instance.manager.current = target_screen_name
        target_screen = screen_instance.manager.get_screen(target_screen_name)
        if hasattr(target_screen, 'refresh_ui'):
            target_screen.refresh_ui()

    layout = BoxLayout(orientation="vertical")
    
    lbl = Label(text=f"{name} shop", size_hint=(1, None), height=dp(50), font_size='20sp', bold=True)
    layout.add_widget(lbl)

    _layout = GridLayout(cols=len(btn_arr), rows=1, size_hint=(1, 0.2), spacing=dp(5), padding=dp(5))
    layout.add_widget(_layout)
    
    for d in range(len(btn_arr)):
        btn = Button(text=f"{btn_arr[d][0]}")
        btn.bind(on_press=partial(btn_arr[d][1], screen_instance, name))
        _layout.add_widget(btn)
    
    # Data Area
    if len(array) <= 0:
        lbl2 = Label(text="No items available", color=(1, 0, 0, 1))
        layout.add_widget(lbl2)
    else:
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        no = len(array) + 1
        grider = GridLayout(cols=6, rows=no, spacing=dp(2), padding=dp(2), size_hint_y=None)
        grider.bind(minimum_height=grider.setter('height'))
        scroll.add_widget(grider)
        layout.add_widget(scroll)
        
        # Headers
        for j in heads:
            hd = Label(text=f"{j}", color=(0, 0, 1, 1), bold=True, size_hint_y=None, height=dp(40))
            grider.add_widget(hd)
            
        # Data Rows
        for d in range(len(array)):
            grider.add_widget(Label(text=f"{d+1}", color=(0, 1, 0, 1), size_hint_y=None, height=dp(40))) 
            for i in range(len(array[d])):
                grider.add_widget(Label(text=f"{array[d][i]}", size_hint_y=None, height=dp(40)))

    # Bottom area (Navigation Bar)
    btm_layout = GridLayout(rows=1, cols=3, size_hint=(1, None), height=dp(50), padding=dp(5), spacing=dp(5))
    layout.add_widget(btm_layout)

    _lbl_ = Label(text=f"{len(array)} records", color=(0, 1, 0, 1))
    btm_layout.add_widget(_lbl_)
    
    home_btn = Button(text="Home", background_color=(0.8, 0.8, 0.8, 1), color=(0,0,0,1))
    home_btn.bind(on_press=lambda instance: switch_and_refresh("home"))
    btm_layout.add_widget(home_btn)

    # Dynamic Shop Switcher
    if name in ['store']:
        switch_box = BoxLayout(orientation='horizontal', spacing=dp(5))
        
        btn_agg = Button(text="Aggrey", font_size='12sp')
        # FIXED: Using the helper function to switch and refresh
        btn_agg.bind(on_press=lambda instance: switch_and_refresh("aggrey"))
        
        btn_ddc = Button(text="DDC", font_size='12sp')
        btn_ddc.bind(on_press=lambda instance: switch_and_refresh("ddc"))
        
        switch_box.add_widget(btn_agg)
        switch_box.add_widget(btn_ddc)
        btm_layout.add_widget(switch_box)
        
    elif name in ['Aggrey']:
        switch_box = BoxLayout(orientation='horizontal', spacing=dp(5))
        btn_str = Button(text="Store", font_size='12sp')
        btn_str.bind(on_press=lambda instance: switch_and_refresh("store"))
        btn_ddc = Button(text="DDC", font_size='12sp')
        btn_ddc.bind(on_press=lambda instance: switch_and_refresh("ddc"))
        switch_box.add_widget(btn_str)
        switch_box.add_widget(btn_ddc)
        btm_layout.add_widget(switch_box)

    elif name in ['DDC']:
        switch_box = BoxLayout(orientation='horizontal', spacing=dp(5))
        btn_str = Button(text="Store", font_size='12sp')
        btn_str.bind(on_press=lambda instance: switch_and_refresh("store"))
        btn_agg = Button(text="Aggrey", font_size='12sp')
        btn_agg.bind(on_press=lambda instance: switch_and_refresh("aggrey"))
        switch_box.add_widget(btn_str)
        switch_box.add_widget(btn_agg)
        btm_layout.add_widget(switch_box)

    return layout
        
# --- SCREEN CLASSES ---

class homeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
        self.add_widget(layout)

        lbl = Label(text="Kiwali Classic Wear System App", halign="center", font_size='24sp', bold=True)
        layout.add_widget(lbl)

        layout2 = GridLayout(cols=3, rows=1, spacing=dp(10))
        layout.add_widget(layout2)

        btn1 = Button(text="Store", font_size='20sp')
        btn1.bind(on_press=self.store_switch)
        layout2.add_widget(btn1)

        btn2 = Button(text="Aggrey", font_size='20sp')
        btn2.bind(on_press=self.aggrey_switch)
        layout2.add_widget(btn2)

        btn3 = Button(text="DDC", font_size='20sp')
        btn3.bind(on_press=self.ddc_switch)
        layout2.add_widget(btn3)

        layout3 = GridLayout(cols=2, rows=1, spacing=dp(10), size_hint=(1, None), height=dp(60))
        layout.add_widget(layout3)
        
        _btn1 = Button(text="Search", background_color=(0, 1, 0, 1), color=(1,1,1,1))
        _btn1.bind(on_press=self.search_place)
        layout3.add_widget(_btn1)

        _btn2 = Button(text="Quit", background_color=(1, 0, 0, 1), color=(1,1,1,1))
        _btn2.bind(on_press=lambda instance: App.get_running_app().stop()) 
        layout3.add_widget(_btn2)

    # We added a refresh_ui method here to prevent errors if called
    def refresh_ui(self):
        pass 

    def store_switch(self, instance):
        self.manager.current = "store"
        self.manager.get_screen("store").refresh_ui()
        
    def aggrey_switch(self, instance):
        self.manager.current = "aggrey"
        self.manager.get_screen("aggrey").refresh_ui()
        
    def ddc_switch(self, instance):
        self.manager.current = "ddc"
        self.manager.get_screen("ddc").refresh_ui()
        
    def search_place(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        inp = TextInput(hint_text="Search keyword in all shops...")
        btn = Button(text="Search")
        
        lbl_res = Label(text="Results...", size_hint_y=None, height=dp(100))
        scroll = ScrollView(); scroll.add_widget(lbl_res)
        
        content.add_widget(inp)
        content.add_widget(btn)
        content.add_widget(scroll)
        
        pop = Popup(title="Global Search", content=content, size_hint=(0.6, 0.6))
        
        def do_global_search(btn):
            kw = inp.text.lower()
            res = []
            for i, x in enumerate(stocks):
                if kw in str(x).lower(): res.append(f"Store #{i+1}: {x}")
            for i, x in enumerate(aggr):
                if kw in str(x).lower(): res.append(f"Aggrey #{i+1}: {x}")
            for i, x in enumerate(ddc):
                if kw in str(x).lower(): res.append(f"DDC #{i+1}: {x}")
            
            lbl_res.text = "\n".join(res) if res else "Not Found"
            
        btn.bind(on_press=do_global_search)
        pop.open()


class storeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.refresh_ui()
        
    def refresh_ui(self):
        self.clear_widgets()
        self.add_widget(gui(self, "store", stocks))
    
class aggreyScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.refresh_ui()
        
    def refresh_ui(self):
        self.clear_widgets()
        self.add_widget(gui(self, "Aggrey", aggr))

class ddcScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.refresh_ui()
        
    def refresh_ui(self):
        self.clear_widgets()
        self.add_widget(gui(self, "DDC", ddc))

class KiwaliApp(App):
    def build(self):
        scr = ScreenManager()
        scr.add_widget(homeScreen(name="home"))
        scr.add_widget(storeScreen(name="store"))
        scr.add_widget(aggreyScreen(name="aggrey"))
        scr.add_widget(ddcScreen(name="ddc"))
        return scr
    
if __name__=='__main__':
    KiwaliApp().run()