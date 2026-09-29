from tkinter import messagebox
import numpy as np
import pandas as pd
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.optimize import curve_fit
import os

window = Tk()
window.title("Elek Analizi")
window.minsize(500,550)
window.config(bg="white")
window.config(pady=30,padx=30)

main_label = Label(window,text="ELEK ANALİZİ HESAPLAMALARI",font=("Arial",12,"bold"))
main_label.grid(row=0,column=0,columnspan=2,pady=15)

dosya_adi = "Elek Analizi.xlsx"

if os.path.exists(dosya_adi):
    df = pd.read_excel(dosya_adi)

else:
    df = pd.DataFrame({
        "Elek Boyutu (mm)": [4.70, 2.36, 1.18, 0.60, 0.30],
        "Kalan (g)": [50, 80, 120, 100, 70]
    })
    df.to_excel(
        dosya_adi,
        index=False
    )
    messagebox.showinfo("Dosya Oluşturuldu","Elek Analizi.xlsx dosyası oluşturuldu.")
    df = pd.read_excel("Elek Analizi.xlsx")

df = df.sort_values(
    by="Elek Boyutu (mm)",
    ascending=False
).reset_index(drop=True)

toplam =df["Kalan (g)"].sum()
df["Miktar (%)"] = 100 * df["Kalan (g)"] / toplam
df["Kümülatif Elek Altı"] = (df["Miktar (%)"].iloc[::-1].cumsum().iloc[::-1].shift(-1).fillna(0))

x=df["Elek Boyutu (mm)"].to_numpy(dtype=float)
y=df["Kümülatif Elek Altı"].to_numpy(dtype=float)

gecerli = (
    np.isfinite(x)
    & np.isfinite(y)
    & (x > 0)
    & (y > 0)
    & (y < 100)
)

x_fit = x[gecerli]
y_fit = y[gecerli]

def gaudin_schuhmann(x, k, m):
    return 100 * (x / k) ** m

params, covariance = curve_fit(gaudin_schuhmann,x_fit,y_fit,p0=[10, 1],bounds=([0.0001, 0.0001],[np.inf, np.inf]))
k, m = params

d_degeri_label = Label(window,text="Yüzde değeri girin")
d_degeri_label.grid(row=1,column=0,columnspan=2,pady=15)

d_degeri_entry = Entry(window,width=40)
d_degeri_entry.grid(row=1,column=2,pady=15)

def dxx_hesapla(yuzde):
    return k * (yuzde / 100) ** (1 / m)

D50 = dxx_hesapla(50)
D80 = dxx_hesapla(80)

def d_hesapla():
    try:
        yuzde = float(d_degeri_entry.get())
        if yuzde <= 0 or yuzde >= 100:
            d_degeri_sonuc.config(text="Lütfen 0 ile 100 arasında değer girin.")
            return
        d_degeri = dxx_hesapla(yuzde)
        d_degeri_sonuc.config(text=(f"%{yuzde:.0f} için tane boyutu = "f"{d_degeri:.4f} mm"))

    except ValueError:
        d_degeri_sonuc.config(text="Lütfen geçerli bir sayı girin.")


d_degeri_button = Button(window,text="Hesapla",command=d_hesapla)
d_degeri_button.grid(row=2,column=0,columnspan=2,pady=15)

d_degeri_sonuc = Label(window,text="---------------------")
d_degeri_sonuc.grid(row=3,column=0,columnspan=2,pady=15)

x_model = np.logspace(
    np.log10(x_fit.min()),
    np.log10(x_fit.max()),
    300
)

y_model = gaudin_schuhmann(
    x_model,
    k,
    m
)
# Grafik

plt.figure(figsize=(9, 6))

plt.xscale("log")
plt.yscale("log")

def normal_sayi(x, pos):
    if x >= 1:
        return f"{x:g}"
    elif x >= 0.01:
        return f"{x:.2f}".rstrip("0").rstrip(".")
    else:
        return f"{x:.3f}".rstrip("0").rstrip(".")

ax = plt.gca()

ax.xaxis.set_major_formatter(FuncFormatter(normal_sayi))
ax.xaxis.set_minor_formatter(FuncFormatter(normal_sayi))

ax.yaxis.set_major_formatter(FuncFormatter(normal_sayi))
ax.yaxis.set_minor_formatter(FuncFormatter(normal_sayi))

plt.scatter(
    x_fit,
    y_fit,
    label="Elek Analizi"
)

# Gaudin-Schuhmann eğrisi
plt.plot(
    x_model,
    y_model,
    linewidth=2,
    label="Gaudin-Schuhmann"
)

# D50
plt.axhline(50, linestyle="--", linewidth=1)
plt.axvline(D50, linestyle="--", linewidth=1)

plt.scatter(D50, 50, s=40)

plt.annotate(
    f"D50 = {D50:.4f} mm",
    (D50, 50),
    xytext=(5, -10),
    textcoords="offset points"
)

# D80
plt.axhline(80, linestyle="--", linewidth=1)
plt.axvline(D80, linestyle="--", linewidth=1)

plt.scatter(D80, 80, s=40)

plt.annotate(
    f"D80 = {D80:.4f} mm",
    (D80, 80),
    xytext=(5, -10),
    textcoords="offset points"
)

plt.xlabel("Elek Açıklığı (mm)")
plt.ylabel("Kümülatif Elek Altı (%)")

plt.title("Elek Analizi - Gaudin-Schuhmann")

plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

plt.show(block=False)

window.mainloop()


