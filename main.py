import json
import os
from datetime import datetime

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.screen import MDScreen

KV = '''
ScreenManager:
    Beranda:
    Riwayat:

<Beranda>:
    name: "beranda"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.12, 0.15, 0.25, 1

        MDTopAppBar:
            title: "KASIR KEUANGAN"
            md_bg_color: 0.2, 0.6, 0.9, 1
            specific_text_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"

            MDCard:
                orientation: "vertical"
                size_hint_y: None
                height: "160dp"
                padding: "20dp"
                spacing: "10dp"
                md_bg_color: 0.15, 0.35, 0.6, 1
                elevation: 8
                radius: [15, ]

                MDLabel:
                    id: saldo_text
                    text: "SALDO: Rp 0"
                    font_size: "26sp"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

                MDBoxLayout:
                    spacing: "10dp"

                    MDLabel:
                        id: masuk_text
                        text: "Masuk: Rp 0"
                        font_size: "15sp"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.7, 1, 0.7, 1

                    MDLabel:
                        id: keluar_text
                        text: "Keluar: Rp 0"
                        font_size: "15sp"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 0.7, 0.7, 1

            MDTextField:
                id: keterangan
                hint_text: "Keterangan (contoh: Gaji, Belanja...)"
                icon_right: "text"

            MDTextField:
                id: jumlah
                hint_text: "Jumlah (Rp)"
                icon_right: "cash"
                input_filter: "float"

            MDBoxLayout:
                adaptive_height: True
                spacing: "15dp"

                MDRaisedButton:
                    text: "PEMASUKAN"
                    size_hint_x: 1
                    md_bg_color: 0.2, 0.8, 0.4, 1
                    on_release: app.tambah_transaksi("masuk")

                MDRaisedButton:
                    text: "PENGELUARAN"
                    size_hint_x: 1
                    md_bg_color: 0.9, 0.3, 0.3, 1
                    on_release: app.tambah_transaksi("keluar")

            MDRaisedButton:
                text: "LIHAT RIWAYAT"
                pos_hint: {"center_x": 0.5}
                on_release: root.manager.current = "riwayat"

            Widget:

<Riwayat>:
    name: "riwayat"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.12, 0.15, 0.25, 1

        MDTopAppBar:
            title: "RIWAYAT TRANSAKSI"
            md_bg_color: 0.2, 0.6, 0.9, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, "current", "beranda")]]

        ScrollView:
            MDList:
                id: daftar
'''


class Beranda(MDScreen):
    pass


class Riwayat(MDScreen):
    pass


class KasirApp(MDApp):
    dialog = None

    # ---------- Data ----------
    def path_data(self):
        # user_data_dir adalah folder yang boleh ditulis di Android
        return os.path.join(self.user_data_dir, "data_keuangan.json")

    def muat_data(self):
        try:
            with open(self.path_data(), "r") as f:
                return json.load(f)
        except Exception:
            return []

    def simpan_data(self, data):
        with open(self.path_data(), "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def rupiah(angka):
        # 1,500,000 -> 1.500.000
        return f"{angka:,.0f}".replace(",", ".")

    # ---------- App ----------
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        self.update_ringkasan()
        self.update_riwayat()

    def tambah_transaksi(self, jenis):
        ids = self.root.get_screen("beranda").ids
        keterangan = ids.keterangan.text.strip()
        jumlah_text = ids.jumlah.text.strip()

        if not keterangan or not jumlah_text:
            self.tampilkan_pesan("Isi semua kolom!")
            return

        try:
            jumlah = float(jumlah_text)
        except ValueError:
            self.tampilkan_pesan("Masukkan angka yang benar!")
            return

        if jumlah <= 0:
            self.tampilkan_pesan("Jumlah harus lebih dari 0!")
            return

        data = self.muat_data()
        data.append({
            "jenis": jenis,
            "jumlah": jumlah,
            "keterangan": keterangan,
            "tanggal": datetime.now().strftime("%d/%m %H:%M"),
        })
        self.simpan_data(data)

        ids.keterangan.text = ""
        ids.jumlah.text = ""

        self.update_ringkasan()
        self.update_riwayat()
        self.tampilkan_pesan("Tersimpan!")

    def update_ringkasan(self):
        data = self.muat_data()
        total_masuk = sum(t["jumlah"] for t in data if t["jenis"] == "masuk")
        total_keluar = sum(t["jumlah"] for t in data if t["jenis"] == "keluar")
        saldo = total_masuk - total_keluar

        ids = self.root.get_screen("beranda").ids
        ids.saldo_text.text = f"SALDO: Rp {self.rupiah(saldo)}"
        ids.masuk_text.text = f"Masuk: Rp {self.rupiah(total_masuk)}"
        ids.keluar_text.text = f"Keluar: Rp {self.rupiah(total_keluar)}"

    def update_riwayat(self):
        daftar = self.root.get_screen("riwayat").ids.daftar
        daftar.clear_widgets()
        data = self.muat_data()

        if not data:
            daftar.add_widget(OneLineListItem(text="Belum ada transaksi"))
            return

        for t in reversed(data):
            tanda = "+" if t["jenis"] == "masuk" else "-"
            teks = f"{t['tanggal']} | {t['keterangan']} | {tanda}Rp {self.rupiah(t['jumlah'])}"
            daftar.add_widget(OneLineListItem(text=teks))

    def tampilkan_pesan(self, pesan):
        if not self.dialog:
            self.dialog = MDDialog(
                text=pesan,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss(),
                    )
                ],
            )
        else:
            self.dialog.text = pesan
        self.dialog.open()


if __name__ == "__main__":
    KasirApp().run()
