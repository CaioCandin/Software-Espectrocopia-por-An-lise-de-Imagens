import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import colour
from colour.plotting import *
from scipy.signal import find_peaks

class EspectroscopiaApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1200x628')
        self.root.title('Software de Espectroscopia')
        self.root.configure(bg='#f0f0f0')
        
        self.img_arr = None
        self.fig = None
        self.canvas = None
        self.toolbar = None
        
        self.criar_interface()
        
    def criar_interface(self):
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.botoes_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        self.botoes_frame.pack(pady=10)

        self.botao1 = tk.Button(
        self.botoes_frame,
        text='Espectro RGB',
        command=self.plotar_espectro_rgb,
        )
        self.botao1.grid(row=0, column=0, padx=5)

        self.botao2 = tk.Button(
            self.botoes_frame,
            text='Espectro continuo',
            command=self.plotar_espectro_continuo,
        )
        self.botao2.grid(row=0, column=1, padx=5)

        self.botao3 = tk.Button(
            self.botoes_frame,
            text='Espectro Smits',
            command=self.plotar_espectro_Smits
        )
        self.botao3.grid(row=0, column=2, padx=5)

        self.botao4 = tk.Button(
            self.botoes_frame,
            text='Gaussiana Ideal',
            command=self.plotar_gaussiana
        )
        self.botao4.grid(row=0, column=3, padx=5)

        self.botao5 = tk.Button(
            self.botoes_frame,
            text='Gray Scale',
            command=self.plotar_escala_cinza
        )
        self.botao5.grid(row=0, column=4, padx=5)

        self.botao6 = tk.Button(
            self.botoes_frame,
            text='Exportar Dados',
            command=self.exportar_dados
        )
        self.botao6.grid(row=0, column=5, padx=5)
        
        self.botao7 = tk.Button(
            self.botoes_frame,
            text='CMFS (CIE 1931)',
            command=self.plot_single_cmfs
        )
        self.botao7.grid(row=0, column=6, padx=5)

        self.frame_graph = tk.Frame(self.main_frame, bg='white', highlightbackground="gray", highlightthickness=1)
        self.frame_graph.pack(fill=tk.BOTH, expand=True)
        self.status_frame = ttk.Frame(self.root)

        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(
            self.status_frame,
            text="",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.label_imagem = tk.Label(self.main_frame)
        self.label_imagem.pack()

    def plot_single_cmfs(self):
        plot_single_cmfs(
            "CIE 1931 2 Degree Standard Observer",
            y_label="Sensitivity",
            bounding_box=(390, 870, 0, 1.1),
        )
        
    def carregar_imagem(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.png *.jpeg"), ("Todos arquivos", "*.*")]
        )
        if not filename:
            return
        
        self.img_arr = cv2.imread(filename)
        self.img_arr = cv2.cvtColor(self.img_arr, cv2.COLOR_BGR2RGB)
        self.img_arr = cv2.GaussianBlur(self.img_arr, (5,5), 0)
        
        self.img = Image.fromarray(self.img_arr)

        imagetk = ImageTk.PhotoImage(image=self.img)                
        self.label_imagem.config(image=imagetk)
        self.label_imagem.image = imagetk    
            
    def plotar_espectro_rgb(self):
            
        self.carregar_imagem()
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()
        
        self.altura, self.largura, _ = self.img_arr.shape
        self.comprimentos_onda_mapeados = np.linspace(380, 780, self.largura)
        self.espectro_r = [np.mean(self.img_arr[:, x, 0])/255 for x in range(self.largura)]
        self.espectro_g = [np.mean(self.img_arr[:, x, 1])/255 for x in range(self.largura)]
        self.espectro_b = [np.mean(self.img_arr[:, x, 2])/255 for x in range(self.largura)]
         
        self.fig = plt.Figure(figsize=(9, 4))
        ax = self.fig.add_subplot(111)
                
        ax.plot(self.espectro_r, color = 'red')#, label="Vermelho (R)")
        ax.plot(self.espectro_g, color = 'green')#, label="Verde (G)")
        ax.plot(self.espectro_b, color='blue')#, label="Azul (B)")
            
        ax.set_title("Espectroscopia RGB da Imagem", fontsize=12)
        ax.set_xlabel("Posição Horizontal na Imagem")
        ax.set_ylabel("Intensidade Normalizada")
        ax.legend()
        ax.grid(True)
            
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph)
        self.toolbar.update()

    def plotar_espectro_continuo(self):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()
        
        try:            
            
            ls = colour.SDS_LIGHT_SOURCES["Mercury"].align(colour.SpectralShape(380, 780,((780.0 - 380.0) / (float(self.largura) - 1.0))))
            mercurio = ls.values

            self.cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
            self.wavelengths = self.cmfs.wavelengths
            s_r = self.cmfs.values[:, 0]
            s_g = self.cmfs.values[:, 1]
            s_b = self.cmfs.values[:, 2]
            
            self.s_r_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_r)
            self.s_g_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_g)
            self.s_b_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_b)

            self.espectro = (self.espectro_r * self.s_r_interp + self.espectro_g * self.s_g_interp + self.espectro_b * self.s_b_interp)

            self.picos, _ = find_peaks(self.espectro, prominence=0.1, width=5)
            
            comprimento_onda, intensidade = self.carregar_txt_espectro()            
            comprimento_onda_the, intensidade_the = self.carregar_txt_the()

            self.fig = plt.Figure(figsize=(9, 4), dpi=100)
            ax = self.fig.add_subplot(111)

            if comprimento_onda is not None and intensidade is not None:
                comprimento_onda_interp = np.linspace(
                    comprimento_onda.min(),
                    comprimento_onda.max(),
                    self.largura
                )

                intensidade_interp = np.interp(
                    comprimento_onda_interp,
                    comprimento_onda,
                    intensidade
                )

                ax.plot(comprimento_onda_interp, (intensidade_interp / np.max(intensidade_interp)), 
                        color='red', label='Espectro "Teórico"')

            if comprimento_onda_the is not None and intensidade_the is not None:
                comprimento_onda_interp_the = np.linspace(
                    comprimento_onda_the.min(),
                    comprimento_onda_the.max(),
                    self.largura
                )

                intensidade_interp_the = np.interp(
                    comprimento_onda_interp_the,
                    comprimento_onda_the,
                    intensidade_the
                )

                ax.plot(comprimento_onda_interp_the, 
                        (intensidade_interp_the / np.max(intensidade_interp_the)), 
                        color='black', label='Espectro Theremino')
            ax.plot(self.comprimentos_onda_mapeados, self.espectro, color='darkviolet', label = 'Espectro Obtido')
            ax.plot(self.comprimentos_onda_mapeados, (mercurio / np.max(mercurio))/2.5, 'b--', label='Mercúrio (Referência)')
            ax.scatter(self.comprimentos_onda_mapeados[self.picos], self.espectro[self.picos], color='black')
            ax.set(xlabel='Comprimento de Onda (nm)', ylabel='Intensidade Relativa',
                   title='Reconstrução Espectral via RGB + CIE 1931')
            ax.legend()
            ax.grid(alpha=0.3)
                        
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph)
            self.toolbar.update()

        except Exception as e:
            tk.messagebox.showerror("Erro", f"Falha ao gerar espectro contínuo:\n{str(e)}")

    def plotar_espectro_Smits(self):
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()

        try:
            img_rgb = cv2.cvtColor(self.img_arr, cv2.COLOR_BGR2RGB)
            img_linear = colour.models.eotf_inverse_sRGB(img_rgb)
    
            step = (780.0 - 380.0) / (float(self.largura) - 1.0)
            shape = colour.SpectralShape(380, 780, step)           
            espectros = []
            
            for x in range(self.largura):
                coluna = img_linear[:, x, :]
                media_rgb = np.mean(coluna, axis=0)
                XYZ = colour.RGB_to_XYZ(media_rgb, colour.models.RGB_COLOURSPACES['sRGB'])
                espectro_sd = colour.XYZ_to_sd(XYZ, method='Jakob 2019', shape=shape)
                espectro_alinhado = espectro_sd.align(shape)
                espectros.append(espectro_alinhado.values)

            espectros = np.array(espectros)
            espectro_medio = np.mean(espectros, axis=0)
            espectro_medio /= np.max(espectro_medio)  
            
            ls = colour.SDS_LIGHT_SOURCES["Mercury"].align(shape)
            mercurio = ls.values

            indices_teoricos, _ = find_peaks(mercurio, height=0.1)
            picos_teoricos = ls.domain[indices_teoricos]

            indices_medido, _ = find_peaks(espectro_medio, height=0.1)
            picos_medido = ls.domain[indices_medido]

            if len(picos_teoricos) == len(picos_medido):
                deslocamento = np.mean(picos_medido - picos_teoricos)
                wavelengths_calibrado = ls.domain - deslocamento
            else:
                wavelengths_calibrado = ls.domain  
            
            
            self.fig = plt.Figure(figsize=(9, 4), dpi=100)
            n = min(len(wavelengths_calibrado), len(espectro_medio))
            ax = self.fig.add_subplot(111)
            ax.plot(wavelengths_calibrado[:n], espectro_medio[:n][::-1], 'r-', label='Espectro Estimado (Calibrado)')
            ax.plot(self.comprimentos_onda_mapeados[:n], mercurio[:n], 'b--', label='Mercúrio (Referência)')
            ax.set(xlabel='Comprimento de Onda (nm)', ylabel='Intensidade Relativa',
                   title='Reconstrução Espectral via RGB + Calibração com Mercúrio')
            ax.legend()
            ax.grid(alpha=0.3)

            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph)
            self.toolbar.update()

        except Exception as e:
            tk.messagebox.showerror("Erro", f"Falha ao gerar espectro contínuo:\n{e}")
            
    def plotar_gaussiana(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()

        try:
            ls = colour.SDS_LIGHT_SOURCES["Mercury"].align(
                colour.SpectralShape(380, 780, ((780.0 - 380.0) / (float(self.largura) - 1.0)))
            )
            mercurio = ls.values

            self.cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
            self.wavelengths = self.cmfs.wavelengths
            s_r = self.cmfs.values[:, 0]
            s_g = self.cmfs.values[:, 1]
            s_b = self.cmfs.values[:, 2]

            self.s_r_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_r)
            self.s_g_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_g)
            self.s_b_interp = np.interp(self.comprimentos_onda_mapeados, self.wavelengths, s_b)

            self.espectro = (
                self.espectro_r * self.s_r_interp +
                self.espectro_g * self.s_g_interp +
                self.espectro_b * self.s_b_interp
            )

            self.picos, _ = find_peaks(self.espectro, prominence=0.1, width=5)

            self.fig = plt.Figure(figsize=(9, 4), dpi=100)
            ax = self.fig.add_subplot(111)


            comprimento_onda, intensidade = self.carregar_txt_espectro()            
            comprimento_onda_the, intensidade_the = self.carregar_txt_the()

            self.fig = plt.Figure(figsize=(9, 4), dpi=100)
            ax = self.fig.add_subplot(111)

            if comprimento_onda is not None and intensidade is not None:
                comprimento_onda_interp = np.linspace(
                    comprimento_onda.min(),
                    comprimento_onda.max(),
                    self.largura
                )

                intensidade_interp = np.interp(
                    comprimento_onda_interp,
                    comprimento_onda,
                    intensidade
                )

                ax.plot(comprimento_onda_interp, (intensidade_interp / np.max(intensidade_interp)), 
                        color='red', label='Espectro "Teórico"')

            if comprimento_onda_the is not None and intensidade_the is not None:
                comprimento_onda_interp_the = np.linspace(
                    comprimento_onda_the.min(),
                    comprimento_onda_the.max(),
                    self.largura
                )

                intensidade_interp_the = np.interp(
                    comprimento_onda_interp_the,
                    comprimento_onda_the,
                    intensidade_the
                )

                ax.plot(comprimento_onda_interp_the, 
                        (intensidade_interp_the / np.max(intensidade_interp_the)), 
                        color='black', label='Espectro Theremino')
                                
            idx_max = np.argmax(self.espectro)
            pico_max = self.comprimentos_onda_mapeados[idx_max]

            largura = 45
            espectro_gauss = np.exp(-0.5 * ((self.comprimentos_onda_mapeados - pico_max) / largura) ** 2)

            ax.plot(self.comprimentos_onda_mapeados, (mercurio / np.max(mercurio))/2.5, 'b--', label='Mercúrio (Referência)')
            ax.plot(self.comprimentos_onda_mapeados, espectro_gauss, 'g-', label='Espectro Gaussiano Idealizado')
            ax.scatter(pico_max, 1, color='green', marker='x', label=f'Pico Máx: {pico_max:.1f} nm')  

            ax.set(xlabel='Comprimento de Onda (nm)', ylabel='Intensidade Relativa',
                   title='Reconstrução Espectral via RGB + CIE 1931 + Gaussiana Idealizada')
            ax.legend()
            ax.grid(alpha=0.3)

            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph)
            self.toolbar.update()

        except Exception as e:
            tk.messagebox.showerror("Erro", f"Falha ao gerar espectro contínuo:\n{str(e)}")

    def plotar_escala_cinza(self):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()
        
        try:
            
            ls = colour.SDS_LIGHT_SOURCES["Mercury"]
            ls = ls.align(colour.SpectralShape(380,780, ((780.0 - 380.0) / (float(self.largura) - 1.0))))            
            
            img = cv2.cvtColor(self.img_arr, cv2.COLOR_BGR2GRAY)
            img_linear = colour.models.eotf_inverse_sRGB(img)

            self.img2 = Image.fromarray(img)
            self.img2 = self.img2.resize((775, 45))
            
            imagetk = ImageTk.PhotoImage(image=self.img2)                
            self.label_imagem.config(image=imagetk)
            self.label_imagem.image = imagetk    

            perfil = np.mean(img_linear, axis=0)

            perfil_interp = np.interp(self.comprimentos_onda_mapeados, ls.domain, perfil)
            
            self.fig = plt.Figure(figsize=(9, 4), dpi=100)
            ax = self.fig.add_subplot(111)
            ax.plot(self.comprimentos_onda_mapeados, (perfil_interp / np.max(perfil_interp)), color='gray', label = 'Espectro Cinza Estimado')
            ax.plot(self.comprimentos_onda_mapeados, ls.range,  'b--',label = 'Espectro Mercúrio')
            ax.set(xlabel='Comprimento de Onda (nm)', ylabel='Intensidade Relativa',
                   title='Reconstrução Espectral Gradiente Cinza')
            ax.legend()
            ax.grid(alpha=0.3)
            ax.set_xlim(380, 780)
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph)
            self.toolbar.update()
             
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Falha ao gerar espectro cinza:\n{str(e)}")
    
    def exportar_dados(self):
        self.status_label.config(text="Exportando CSV...")

        self.dados = np.column_stack((self.comprimentos_onda_mapeados, self.espectro))
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_path:
            np.savetxt(file_path, self.dados, delimiter=",", fmt="%.4f")
            self.status_label.config(text=f"CSV exportado: {file_path}")            
    
    def carregar_txt_espectro(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo TXT com os dados do espectro",
            filetypes=[("Arquivos TXT", "*.txt"), ("Todos os arquivos", "*.*")])
        

        if not arquivo:
            print("Nenhum arquivo selecionado.")
            return None, None

        try:
            
            dados = np.loadtxt(arquivo)  
            comprimento_onda = dados[:, 1]  
            intensidade = dados[:, 2]       
            
            return comprimento_onda, intensidade

        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None, None
        
    def carregar_txt_the(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo TXT com os dados do espectro",
            filetypes=[("Arquivos TXT", "*.txt"), ("Todos os arquivos", "*.*")])
        

        if not arquivo:
            print("Nenhum arquivo selecionado.")
            return None, None

        try:
            
            dados = np.loadtxt(arquivo)  
            comprimento_onda = dados[:, 0]  
            intensidade = dados[:, 1]       
            
            return comprimento_onda, intensidade

        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None, None
    
if __name__ == "__main__":
    root = tk.Tk()
    app = EspectroscopiaApp(root)
    root.mainloop()