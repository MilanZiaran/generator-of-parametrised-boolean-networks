from datetime import datetime
from parametrised_bn_gen import generator_of_parametrised_bn
from timeit import default_timer as timer
from tkinter import messagebox, ttk
from tkinter import filedialog as fd

import json
import numpy
import time
import tkinter as tk


# global variables for saving the configuration
seed_val = 0
num_of_nodes_ = 0
l_bound = 0
u_bound = 0
act_frac_reg = 0
MAXSIZE = 2**31-1


def export():
    if selected.get() in [1, 2, 3]:
        if run_checks_and_get_vals(True):
            name = fd.askdirectory()
            if name != "":
                export_json(name + '/')
                messagebox.showinfo('Info', "Configuration saved.")
    else:
        messagebox.showerror('Export Error', "Select a graph generator.")


def export_json(loc_to_save_string: str):
    ba_ = False
    ws_ = False
    rand_ = False
    if selected.get() == 1:
        ba_ = True
        if check_ba_arg():
            ba_conns = int(ba_entry.get())
            ws_conns = "rand"
            ws_prob = "rand"
            rand_prob = "rand"
        else:
            return None
    elif selected.get() == 2:
        ws_ = True
        if check_ws_args():
            ws_conns = int(ws_entry_1.get())
            ws_prob = float(ws_entry_2.get())
            ba_conns = "rand"
            rand_prob = "rand"
        else:
            return None
    else:  # else is sufficient here, because the only option left is selected.get() == 3
        rand_ = True
        if check_prob_for_rand_model():
            rand_prob = float(rand_entry.get())
            ws_conns = "rand"
            ws_prob = "rand"
            ba_conns = "rand"
        else:
            return None
    # https://realpython.com/python-json/
    data = {
        "number of networks": int(num_of_networks.get()),
        "vertices": num_of_nodes_,
        "prob of act reg": act_frac_reg,
        "seed": seed_val,
        "uninterpreted function arity": {
            "lower bound": l_bound,
            "upper bound": u_bound
        },
        "generator": {
            "Barabasi-Albert": {
                "use": ba_,
                "connections": ba_conns
            },
            "Watts-Strogatz": {
                "use": ws_,
                "connections": ws_conns,
                "rewire probability": ws_prob
            },
            "Random Network": {
                "use": rand_,
                "connection probability": rand_prob
            }
        }
    }
    try:
        with open(f"{loc_to_save_string}configuration_{datetime.now().strftime('%y%m%d%H%M%S')}.json", 'w') as j:
            json.dump(data, j, indent=4)
    except PermissionError:
        messagebox.showerror('Permission Error', f"Permission denied for {loc_to_save_string}")


def check_seed():
    if seed.get() != "":
        try:
            if int(seed.get()) < 0:
                messagebox.showerror('Seed Error', "Seed value is lower than 0.")
                return False
            elif int(seed.get()) > MAXSIZE:
                messagebox.showerror('Seed Error', "Seed value exceeds 2^32-1")
                return False
        except ValueError:
            messagebox.showerror('Seed Error', "Seed value is invalid.")
            return False
    return True


def check_l_bound():
    if lower_bound.get() != "":
        try:
            if int(lower_bound.get()) < 1:
                messagebox.showerror('Lower Bound Error', "Lower bound is lower than 1.")
                return False
            elif int(lower_bound.get()) > MAXSIZE:
                messagebox.showerror('Lower Bound Error', "Lower bound exceeds 2^32-1")
                return False
        except ValueError:
            messagebox.showerror('Lower Bound Error', "Lower bound is invalid.")
            return False
    return True


def check_u_bound():
    if upper_bound.get() != "":
        try:
            if int(upper_bound.get()) < 1:
                messagebox.showerror('Upper Bound Error', "Upper bound is lower than 1.")
                return False
            elif int(upper_bound.get()) > MAXSIZE:
                messagebox.showerror('Upper Bound Error', "Upper bound exceeds 2^32-1")
                return False
        except ValueError:
            messagebox.showerror('Upper Bound Error', "Upper bound is invalid.")
            return False
    return True


def check_boundaries():
    if check_u_bound() and check_l_bound():
        if upper_bound.get() != "" and lower_bound.get() != "":
            if int(upper_bound.get()) >= int(lower_bound.get()):
                return True
            messagebox.showerror('Boundaries Error', "Upper bound is lower than lower bound.")
            return False
        return True
    return False


def check_vertices():
    if num_of_vertices_entry.get() != "":
        try:
            if int(num_of_vertices_entry.get()) < 2:
                messagebox.showerror('Number of Vertices Error', "Number of vertices is lower than 2.")
                return False
            elif int(num_of_vertices_entry.get()) > MAXSIZE:
                messagebox.showerror('Number of Vertices Error', "Number of vertices exceeds 2^32-1")
                return False
        except ValueError:
            messagebox.showerror('Number of Vertices Error', "Number of vertices is invalid.")
            return False
    return True


def check_networks():
    if num_of_networks.get() != "":
        try:
            if int(num_of_networks.get()) < 1:
                messagebox.showerror('Number of Networks Error', "Number of networks is lower than 1.")
                return False
            elif int(num_of_networks.get()) > MAXSIZE:
                messagebox.showerror('Number of Networks Error', "Number of networks exceeds 2^32-1")
                return False
        except ValueError:
            messagebox.showerror('Number of Networks Error', "Number of networks is invalid.")
            return False
    else:
        messagebox.showerror('Number of Networks Error', "Number of networks unfilled.")
        return False
    return True


def check_location():
    if loc_file['text'] == "":
        messagebox.showerror('Directory Error', "No directory to save the network was provided.")
        return False
    return True


def check_select():
    if selected.get() == 0:
        messagebox.showerror('Error', "Please select a model.")
        return False
    return True


def check_prob_for_rand_model():
    try:
        if float(rand_entry.get()) <= 0 or float(rand_entry.get()) > 1:
            messagebox.showerror('Probability Error', "Probability for random model is out of range (0,1].")
            return False
    except ValueError:
        messagebox.showerror('Probability Error', "Probability for random model is invalid.")
        return False
    return True


def check_ws_arg_1():
    try:
        if int(ws_entry_1.get()) < 2:
            messagebox.showerror('Watts-Strogatz Error', "Number of connections for is less than 2.")
            return False
        if num_of_vertices_entry.get() != "":
            if int(ws_entry_1.get()) > int(num_of_vertices_entry.get()):
                messagebox.showerror('Watts-Strogatz Error', "Number of vertices is lower than number of connections.")
                return False
        if int(ws_entry_1.get()) > MAXSIZE:
            messagebox.showerror('Watts-Strogatz Error', "Number of connections exceeds 2^32-1")
            return False
    except ValueError:
        messagebox.showerror('Watts-Strogatz Error', "Number of connections is invalid.")
        return False
    return True


def check_ws_arg_2():
    try:
        if float(ws_entry_2.get()) < 0 or float(ws_entry_2.get()) > 1:
            messagebox.showerror('Watts-Strogatz Error', "Probability argument is out of range [0,1].")
            return False
    except ValueError:
        messagebox.showerror('Watts-Strogatz Error', "Probability argument is invalid.")
        return False
    return True


def check_frac_reg():
    if frac_reg.get() != "":
        try:
            if float(frac_reg.get()) < 0 or float(frac_reg.get()) > 1:
                messagebox.showerror('Probability Error', "Fraction of activating regulations is out of range [0,1].")
                return False
        except ValueError:
            messagebox.showerror('Probability Error', "Fraction of activating regulations is invalid.")
            return False
    return True


def check_ws_args():
    if check_ws_arg_1() and check_ws_arg_2():
        if num_of_vertices_entry.get() != "":
            if int(num_of_vertices_entry.get()) < int(ws_entry_1.get()):
                messagebox.showerror('Watts-Strogatz Error', "Number of vertices is lower than number of connections.")
                return False
        return True
    return False


def check_ba_arg():
    try:
        if int(ba_entry.get()) < 1:
            messagebox.showerror('Barábasi-Albert Error', "Number of connections is less than 1.")
            return False
        if num_of_vertices_entry.get() != "":
            if int(ba_entry.get()) >= int(num_of_vertices_entry.get()):
                messagebox.showerror('Barábasi-Albert Error', "Number of vertices is lower than or "
                                                              "equal to the number of connections.")
                return False
        if int(ba_entry.get()) > MAXSIZE:
            messagebox.showerror('Barábasi-Albert Error', "Number of connections exceeds 2^32-1")
            return False
    except ValueError:
        messagebox.showerror('Barábasi-Albert Error', "Number of connections is invalid.")
        return False
    return True


def check_frac_and_or():
    if frac_and_or.get() != "":
        try:
            if float(frac_and_or.get()) < 0 or float(frac_and_or.get()) > 1:
                messagebox.showerror('Probability Error', "Fraction of ANDs and ORs is out of range [0,1].")
                return False
        except ValueError:
            messagebox.showerror('Probability Error', "Fraction of ANDs and ORs is invalid.")
            return False
    return True


def run_checks_and_get_vals(export: bool):
    # w3schools.com/python/python_variables_global.asp
    global seed_val, num_of_nodes_, l_bound, u_bound, act_frac_reg
    if check_select() and check_seed() and check_boundaries() and \
            check_vertices() and check_networks() and (export or check_location()) and check_frac_reg():
        if seed.get() != "":
            seed_val = int(seed.get())
        elif export and seed_val == 0:
            seed_val = "rand"
        elif not export:
            seed_val = int(time.time())
        if num_of_vertices_entry.get() != "":
            num_of_nodes_ = int(num_of_vertices_entry.get())
        elif export and num_of_nodes_ == 0:
            num_of_nodes_ = "rand"
        if not export:
            if selected.get() == 1:
                if check_ba_arg():
                    if num_of_nodes_ == 0:
                        numpy.random.seed(seed_val)
                        num_of_nodes_ = int(numpy.random.randint(low=int(ba_entry.get()) + 1,
                                                                 high=int(ba_entry.get()) * 10))
                else:
                    return False
            elif selected.get() == 2:
                if check_ws_arg_1():
                    if num_of_nodes_ == 0:
                        numpy.random.seed(seed_val)
                        num_of_nodes_ = int(numpy.random.randint(low=int(ws_entry_1.get()) + 1,
                                                                 high=int(ws_entry_1.get()) * 10))
                else:
                    return False
            else:
                if num_of_nodes_ == 0:
                    numpy.random.seed(seed_val)
                    num_of_nodes_ = int(numpy.random.randint(low=2, high=1000))
        if lower_bound.get() != "":
            l_bound = int(lower_bound.get())
        elif export and l_bound == 0:
            l_bound = "rand"
        elif not export:
            numpy.random.seed(seed_val)
            # trying to set the boundaries as reasonable as possible
            l_bound = int(numpy.random.randint(low=1, high=2 + num_of_nodes_ // 100))
        if upper_bound.get() != "":
            u_bound = int(upper_bound.get())
        elif export and u_bound == 0:
            u_bound = "rand"
        elif not export:
            numpy.random.seed(seed_val)
            u_bound = int(numpy.random.randint(low=l_bound, high=l_bound + 1 + num_of_nodes_ // 100))
        if frac_reg.get() != "":
            act_frac_reg = float(frac_reg.get())
        elif export and act_frac_reg == 0:
            act_frac_reg = "rand"
        elif not export:
            numpy.random.seed(seed_val)
            act_frac_reg = round(numpy.random.random(), 2)
        return True
    return False


def parse_json():
    # datatofish.com/message-box-python/
    msgbox = tk.messagebox.askquestion('Overwrite Configuration', "Are you sure you want "
                                                                  "to overwrite the current configuration?",
                                       icon='warning')
    if msgbox == 'yes':
        name = fd.askopenfilename(filetypes=(("json files", "*.json"), ("all files", "*.*")))
        # are you sure you want to override the current configuration?
        if name != "":  # window was closed by user
            try:
                with open(name, 'r') as jsf:
                    jsn = json.load(jsf)
                    # clear GUI
                    num_of_networks.delete(0, "end")
                    num_of_vertices_entry.delete(0, "end")
                    lower_bound.delete(0, "end")
                    frac_reg.delete(0, "end")
                    seed.delete(0, "end")
                    upper_bound.delete(0, "end")
                    ba_entry.delete(0, "end")
                    ws_entry_1.delete(0, "end")
                    ws_entry_2.delete(0, "end")
                    rand_entry.delete(0, "end")
                    if jsn['number of networks'] != 'rand':
                        num_of_networks.insert(0, jsn['number of networks'])
                    if jsn['vertices'] != 'rand':
                        num_of_vertices_entry.insert(0, jsn['vertices'])
                    if jsn['seed'] != 'rand':
                        seed.insert(0, jsn['seed'])
                    if jsn['prob of act reg'] != 'rand':
                        frac_reg.insert(0, jsn['prob of act reg'])
                    if jsn['uninterpreted function arity']['lower bound'] != 'rand':
                        lower_bound.insert(0, jsn['uninterpreted function arity']['lower bound'])
                    if jsn['uninterpreted function arity']['upper bound'] != 'rand':
                        upper_bound.insert(0, jsn['uninterpreted function arity']['upper bound'])
                    if jsn['generator']['Barabasi-Albert']['use']:
                        ba.invoke()
                        if jsn['generator']['Barabasi-Albert']['connections'] != 'rand':
                            ba_entry.insert(0, jsn['generator']['Barabasi-Albert']['connections'])
                    if jsn['generator']['Watts-Strogatz']['use']:
                        ws.invoke()
                        if jsn['generator']['Watts-Strogatz']['connections'] != 'rand':
                            ws_entry_1.insert(0, jsn['generator']['Watts-Strogatz']['connections'])
                        if jsn['generator']['Watts-Strogatz']['rewire probability'] != 'rand':
                            ws_entry_2.insert(0, jsn['generator']['Watts-Strogatz']['rewire probability'])
                    if jsn['generator']['Random Network']['use']:
                        rand.invoke()
                        if jsn['generator']['Random Network']['connection probability'] != 'rand':
                            rand_entry.insert(0, jsn['generator']['Random Network']['connection probability'])

            except FileNotFoundError:
                messagebox.showerror('File Error', f"File not found {name}")
            except KeyError as e:
                messagebox.showerror('JSON Error', f"JSON is in incorrect form.\n\n {e}")


def generate():
    global u_bound, l_bound
    if selected.get() == 1:
        if run_checks_and_get_vals(False):
            try:
                # measuring speed
                # start = timer()
                generator_of_parametrised_bn.generate_bn(num_of_nodes_, seed=seed_val,
                                                         num_of_connections=int(ba_entry.get()), ba=True,
                                                         l_bound=l_bound, u_bound=u_bound,
                                                         frac_reg=act_frac_reg,
                                                         loc=loc_file['text'] + '/',
                                                         n=int(num_of_networks.get()))
                # end = timer()
                # print(end - start)
                messagebox.showinfo('Info', "Network(s) generated successfully!")
            except Exception:
                messagebox.showerror('Unknown Error', "Unknown error occurred within the generator. "
                                                      "See log file. (logging is not implemented yet)")
    elif selected.get() == 2:
        if run_checks_and_get_vals(False):
            if check_ws_arg_2():
                try:
                    # start = timer()
                    generator_of_parametrised_bn.generate_bn(num_of_nodes_, seed=seed_val,
                                                             num_of_connections=int(ws_entry_1.get()), ws=True,
                                                             l_bound=l_bound, u_bound=u_bound, frac_reg=act_frac_reg,
                                                             probability=float(ws_entry_2.get()),
                                                             loc=loc_file['text'] + '/',
                                                             n=int(num_of_networks.get()))
                    # end = timer()
                    # print(end - start)
                    messagebox.showinfo('Info', "Network(s) generated successfully!")
                except Exception:
                    messagebox.showerror('Unknown Error', "Unknown error occurred within the generator. "
                                                          "See log file. (logging is not implemented yet)")
    elif selected.get() == 3:
        if run_checks_and_get_vals(False):
            if check_prob_for_rand_model():
                try:
                    start = timer()
                    generator_of_parametrised_bn.generate_bn(num_of_nodes_, seed=seed_val,
                                                             probability=float(rand_entry.get()), random=True,
                                                             l_bound=l_bound, u_bound=u_bound, frac_reg=act_frac_reg,
                                                             loc=loc_file['text'] + '/',
                                                             n=int(num_of_networks.get()))
                    end = timer()
                    print(end - start)
                    messagebox.showinfo('Info', "Network(s) generated successfully!")
                except Exception:
                    messagebox.showerror('Unknown Error', "Unknown error occurred within the generator. "
                                                          "See log file. (logging is not implemented yet)")
    elif selected.get() == 4:
        if check_location():
            if check_seed() and check_frac_and_or():
                if frac_and_or.get() != "":
                    frac_and_or_ = frac_and_or.get()
                else:
                    frac_and_or_ = round(numpy.random.random(), 2)
                if seed.get() != "":
                    par_seed = int(seed.get())
                else:
                    par_seed = int(time.time())
                generator_of_parametrised_bn.modify_network(file['text'], parametrisation_frac=frac_and_or_,
                                                            seed=par_seed, loc=loc_file['text'] + '/')
                messagebox.showinfo('Info', "Network(s) generated successfully!")


# an attempt to improve generating multiple networks
# def generate_networks():
#     if check_networks() and check_seed():
#         n = int(num_of_networks.get())
#         numpy.random.seed(int(seed.get()))
#         network_seeds = list(numpy.random.randint(MAXSIZE, size=n))
#         for i in range(n):
#             curr_seed = int(network_seeds[i])
#             generate(curr_seed)
#         messagebox.showinfo('Info', "Network(s) generated successfully!")


def choose_location():
    name = fd.askdirectory()
    if name != "":
        loc_file.configure(text=name, bg="#f9f9f9", wraplength=300)
    # print(name)  # testing


def choose_file_():
    # https://pythonbasics.org/tkinter-filedialog/
    # https://pythonspot.com/tk-file-dialogs/
    name = fd.askopenfilename(filetypes=(("sbml files", "*.sbml"), ("all files", "*.*")))
    if name != "":
        file.configure(text=name, bg="#f9f9f9", wraplength=300)
    # print(name)  # testing


# Disable unavailable options upon choosing a way of generating
def ba_btn():
    num_of_networks['state'] = tk.NORMAL
    lower_bound['state'] = tk.NORMAL
    upper_bound['state'] = tk.NORMAL
    num_of_vertices_entry['state'] = tk.NORMAL
    seed['state'] = tk.NORMAL
    frac_reg['state'] = tk.NORMAL
    frac_and_or['state'] = tk.DISABLED


def ws_btn():
    num_of_networks['state'] = tk.NORMAL
    lower_bound['state'] = tk.NORMAL
    upper_bound['state'] = tk.NORMAL
    num_of_vertices_entry['state'] = tk.NORMAL
    seed['state'] = tk.NORMAL
    frac_reg['state'] = tk.NORMAL
    frac_and_or['state'] = tk.DISABLED


def rand_btn():
    num_of_networks['state'] = tk.NORMAL
    lower_bound['state'] = tk.NORMAL
    upper_bound['state'] = tk.NORMAL
    num_of_vertices_entry['state'] = tk.NORMAL
    seed['state'] = tk.NORMAL
    frac_reg['state'] = tk.NORMAL
    frac_and_or['state'] = tk.DISABLED


def choose_json_btn():
    num_of_networks['state'] = tk.DISABLED
    lower_bound['state'] = tk.DISABLED
    upper_bound['state'] = tk.DISABLED
    num_of_vertices_entry['state'] = tk.DISABLED
    seed['state'] = tk.DISABLED
    frac_reg['state'] = tk.DISABLED
    frac_and_or['state'] = tk.DISABLED


def choose_net_btn():
    num_of_networks['state'] = tk.DISABLED
    lower_bound['state'] = tk.DISABLED
    upper_bound['state'] = tk.DISABLED
    num_of_vertices_entry['state'] = tk.DISABLED
    seed['state'] = tk.NORMAL
    frac_reg['state'] = tk.DISABLED
    frac_and_or['state'] = tk.NORMAL


window = tk.Tk()

content = ttk.Frame(window, padding=(3, 3, 12, 12))

gen_prop = tk.Label(content, text="Generator Properties")
gen_prop.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
gen_prop.config(font=('Helvetica', 15))

net_prop = tk.Label(content, text="Network Properties")
net_prop.grid(column=2, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
net_prop.config(font=('Helvetica', 15))

choose = tk.Label(content, text="Choose a model:")
choose.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
choose.config(font=('Helvetica', 12))

var = tk.StringVar()
selected = tk.IntVar()

# https://likegeeks.com/python-gui-examples-tkinter-tutorial/#Add_radio_buttons_widgets
ba = tk.Radiobutton(content, text="Barabási-Albert model", command=ba_btn,
                    var='ba', value=1, variable=selected)

group_1 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_1, text="Number of existing nodes connected to the newly added node:").grid(row=0, sticky=tk.E)
ba_entry = tk.Entry(group_1)
ba_entry.grid(column=1, row=0, sticky=tk.W)
group_1.grid(column=0, row=3, sticky=tk.N)
group_1.columnconfigure(0, weight=1)

ws = tk.Radiobutton(content, text="Watts-Strogatz model", command=ws_btn,
                    var='ws', value=2, variable=selected)

group_2 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_2, text="Number of nearest neighbours connected to each node:").grid(row=0, sticky=tk.E)
tk.Label(group_2, text="Probability of rewiring each edge (e.g. 0.5):").grid(row=1, sticky=tk.E)
ws_entry_1 = tk.Entry(group_2)
ws_entry_1.grid(column=1, row=0, sticky=tk.W)
ws_entry_2 = tk.Entry(group_2)
ws_entry_2.grid(column=1, row=1, sticky=tk.W)
group_2.grid(column=0, row=5, sticky=tk.N)
group_2.columnconfigure(0, weight=1)

rand = tk.Radiobutton(content, text="Random",
                      var='rand', value=3, variable=selected, command=rand_btn)

group_3 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_3,
         text="Probability that there's an outgoing edge from one vertex to another (e.g. 0.5):").grid(row=0,
                                                                                                       sticky=tk.E)
rand_entry = tk.Entry(group_3)
rand_entry.grid(column=1, row=0, sticky=tk.W)
group_3.grid(column=0, row=7, sticky=tk.N)
group_3.columnconfigure(0, weight=1)

choose_file_opt = tk.Radiobutton(content, text="Modify an existing network", command=choose_net_btn,
                                 var='modify', value=4, variable=selected)

group_6 = tk.LabelFrame(content, padx=15, pady=10)
choose_file = tk.Button(group_6, text="Choose File", width=20, command=choose_file_)
file = tk.Label(group_6)
choose_file.grid(column=1, row=0, sticky=tk.S)
file.grid(column=1, row=1, sticky=tk.N)
group_6.grid(column=0, row=9, sticky=tk.N)
group_6.columnconfigure(0, weight=1)

import_json = tk.Button(content, text="Import configuration from JSON", height=2, width=25, command=parse_json)

group_8 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_8, text="Number of networks to generate:").grid(row=0, sticky=tk.E)
num_of_networks = tk.Entry(group_8)
num_of_networks.grid(column=1, row=0, sticky=tk.W)
group_8.grid(column=2, row=2, sticky=tk.N)
group_8.columnconfigure(0, weight=1)

group_4 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_4, text="*Number of vertices:").grid(row=0, sticky=tk.E)
num_of_vertices_entry = tk.Entry(group_4)
num_of_vertices_entry.grid(column=1, row=0, sticky=tk.W)
group_4.grid(column=2, row=3, sticky=tk.N)
group_4.columnconfigure(0, weight=1)

group_17 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_17, text="*Probability that the regulation is activating (e.g. 0.5):").grid(row=0, sticky=tk.E)
frac_reg = tk.Entry(group_17)
frac_reg.grid(column=1, row=0, sticky=tk.W)
group_17.grid(column=2, row=4, sticky=tk.N)
group_17.columnconfigure(0, weight=1)

group_5 = tk.LabelFrame(content, text="Arity of uninterpreted functions", padx=15, pady=10)
tk.Label(group_5, text="*Lower bound:").grid(row=0, sticky=tk.E)
tk.Label(group_5, text="*Upper bound:").grid(row=1, sticky=tk.E)
lower_bound = tk.Entry(group_5)
upper_bound = tk.Entry(group_5)
lower_bound.grid(column=1, row=0, sticky=tk.W)
upper_bound.grid(column=1, row=1, sticky=tk.W)
group_5.grid(column=2, row=5, sticky=tk.N)
group_5.columnconfigure(0, weight=1)

group_24 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_24, text="*Fraction of ANDs and ORs replaced for parameters (e.g. 0.5):").grid(row=0, sticky=tk.E)
frac_and_or = tk.Entry(group_24)
frac_and_or.grid(column=1, row=0, sticky=tk.W)
group_24.grid(column=2, row=6, sticky=tk.N)
group_24.columnconfigure(0, weight=1)

group_10 = tk.LabelFrame(content, padx=15, pady=10)
tk.Label(group_10, text="*Seed:").grid(row=0, sticky=tk.E)
seed = tk.Entry(group_10)
seed.grid(column=1, row=0, sticky=tk.W)
group_10.grid(column=2, row=7, sticky=tk.N)
group_10.columnconfigure(0, weight=1)

group_9 = tk.LabelFrame(content, text="Location to save the network(s)", padx=15, pady=10)
choose_loc = tk.Button(group_9, text="Choose Directory", width=20, command=choose_location)
loc_file = tk.Label(group_9)
loc_file.grid(column=1, row=1, sticky=tk.N)
choose_loc.grid(column=1, row=0, sticky=tk.S)
group_9.grid(column=2, row=9, sticky=tk.N)
group_9.columnconfigure(0, weight=1)

optional = tk.Label(content, text="Options marked with '*' are optional\n"
                                  "(If left unfilled, they will be randomly generated or default)")
optional.grid(column=2, row=13, sticky=tk.S)

# https://www.geeksforgeeks.org/tkinter-separator-widget/
separator = ttk.Separator(content, orient='vertical')
ex_btn = tk.Button(content, height=2, width=22, text="Export configuration to JSON", command=export)
btn = tk.Button(content, height=2, width=20, text="Generate Network(s)", command=generate)


separator.grid(column=1, row=0, rowspan=15, padx=10, pady=10, sticky=(tk.N, tk.S))
ba.grid(column=0, row=2, sticky=tk.S)
ws.grid(column=0, row=4, sticky=tk.S)
rand.grid(column=0, row=6, sticky=tk.S)
ex_btn.grid(column=2, row=11, sticky=tk.W)
btn.grid(column=2, row=11, sticky=tk.E)
content.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
choose_file_opt.grid(column=0, row=8, sticky=tk.S)
import_json.grid(column=0, row=10, sticky=tk.S)

group_2.columnconfigure(0, weight=1)
group_2.rowconfigure(0, weight=1)

content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=1)
content.columnconfigure(2, weight=1)

content.rowconfigure(0, weight=1)
content.rowconfigure(1, weight=1)
content.rowconfigure(2, weight=1)
content.rowconfigure(3, weight=1)
content.rowconfigure(4, weight=1)
content.rowconfigure(5, weight=1)
content.rowconfigure(6, weight=1)
content.rowconfigure(7, weight=1)
content.rowconfigure(8, weight=1)
content.rowconfigure(9, weight=1)
content.rowconfigure(10, weight=1)
content.rowconfigure(11, weight=1)
content.rowconfigure(12, weight=1)

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

window.title('Generator of Parametrised Boolean Networks')
window.minsize(1100, 600)
# window.resizable(0, 0)
window.mainloop()
