import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
import datetime

# Data structure to store expenses
expenses = {
    "Cartao Nubank": [],
    "Cartao Hiper": [],
    "Cartao Next": []
}

# Função para calcular o valor de uma parcela
def calcular_parcela(total, parcelas):
    return total / parcelas

# Tela para exibir o relatório
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.report_label = Label(text="Relatório de gastos", size_hint=(1, 0.9))
        self.layout.add_widget(self.report_label)

        # Botão para voltar para a tela principal
        self.back_button = Button(text="Voltar", size_hint=(1, 0.1), on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def display_report(self, expenses):
        # Gerar um relatório detalhado
        report = ""
        total_mes_atual = 0
        total_mes_proximo = 0
        total_compras_cartao = {
            "Cartao Nubank": 0,
            "Cartao Hiper": 0,
            "Cartao Next": 0
        }
        total_geral = 0
        pessoas_total_mes_atual = {}

        current_month = datetime.datetime.now().month
        next_month = (current_month % 12) + 1

        for cartao, compras in expenses.items():
            report += f"\nCartão: {cartao}\n"
            for compra in compras:
                pessoa = compra['pessoa']
                parcelas = compra['parcelas']
                valor_parcela = calcular_parcela(compra['total'], parcelas)
                total_compras_cartao[cartao] += compra['total']
                
                # Inicializar o total de cada pessoa se ainda não estiver no dicionário
                if pessoa not in pessoas_total_mes_atual:
                    pessoas_total_mes_atual[pessoa] = 0
                
                # Detalhamento das parcelas por mês (mês atual e próximo)
                for parcela in range(1, parcelas + 1):
                    mes_da_parcela = (current_month + parcela - 1) % 12 or 12

                    if mes_da_parcela == current_month:
                        total_mes_atual += valor_parcela
                        pessoas_total_mes_atual[pessoa] += valor_parcela
                        report += (f"{pessoa} - Parcela {parcela} de {parcelas}: "
                                   f"R${valor_parcela:.2f} (mês atual)\n")
                    elif mes_da_parcela == next_month:
                        total_mes_proximo += valor_parcela
                        report += (f"{pessoa} - Parcela {parcela} de {parcelas}: "
                                   f"R${valor_parcela:.2f} (próximo mês)\n")

        # Exibir o total de cada pessoa no mês atual
        report += "\nResumo por pessoa (mês atual):\n"
        for pessoa, total_pessoa in pessoas_total_mes_atual.items():
            report += f"{pessoa}: R${total_pessoa:.2f}\n"

        # Somar total de cada cartão
        for cartao, total in total_compras_cartao.items():
            report += f"\nTotal de compras no {cartao}: R${total:.2f}"

        # Somar o total geral (todos os cartões)
        total_geral = sum(total_compras_cartao.values())
        report += f"\n\nTotal de compras de todos os cartões: R${total_geral:.2f}\n"

        # Exibir os totais por mês
        report += f"\nMês atual: R${total_mes_atual:.2f}\n"
        report += f"Próximo mês: R${total_mes_proximo:.2f}\n"
        
        self.report_label.text = report

    def go_back(self, instance):
        # Voltar para a tela principal
        self.manager.current = 'main'


# Tela principal para entrada de dados
class ExpenseApp(App):
    def build(self):
        self.sm = ScreenManager()

        # Tela principal
        self.main_screen = Screen(name='main')
        self.main_layout = BoxLayout(orientation='vertical')

        # Seleção de cartão
        self.main_layout.add_widget(Label(text="Selecione o cartao:"))
        self.spinner = Spinner(text="Cartao 1", values=("Cartao Nubank", "Cartao Hiper", "Cartao Next"))
        self.main_layout.add_widget(self.spinner)

        # Nome da pessoa
        self.main_layout.add_widget(Label(text="Nome da pessoa:"))
        self.name_input = TextInput(hint_text="Digite o nome")
        self.main_layout.add_widget(self.name_input)

        # Tipo de compra (A vista ou Parcelado)
        self.main_layout.add_widget(Label(text="Tipo de compra:"))
        self.purchase_type = Spinner(text="A vista", values=("A vista", "Parcelado"))
        self.main_layout.add_widget(self.purchase_type)

        # Número de parcelas (aparece apenas se Parcelado)
        self.main_layout.add_widget(Label(text="Numero de parcelas:"))
        self.installments = TextInput(hint_text="Digite o numero de parcelas")
        self.main_layout.add_widget(self.installments)

        # Valor da compra
        self.main_layout.add_widget(Label(text="Valor TOTAL da compra:"))
        self.amount_input = TextInput(hint_text="Digite o valor")
        self.main_layout.add_widget(self.amount_input)

        # Botão para adicionar compra
        self.add_button = Button(text="Adicionar Compra", on_press=self.add_expense)
        self.main_layout.add_widget(self.add_button)

        # Botão para ver relatório
        self.report_button = Button(text="Ver Relatório", on_press=self.show_report)
        self.main_layout.add_widget(self.report_button)

        self.main_screen.add_widget(self.main_layout)
        self.sm.add_widget(self.main_screen)

        # Tela do relatório
        self.report_screen = ReportScreen(name='report')
        self.sm.add_widget(self.report_screen)

        return self.sm

    def add_expense(self, instance):
        # Lógica para adicionar uma compra e calcular os totais
        cartao = self.spinner.text
        pessoa = self.name_input.text
        tipo_compra = self.purchase_type.text
        valor = float(self.amount_input.text)
        parcelas = int(self.installments.text) if tipo_compra == "Parcelado" else 1

        total = valor

        # Armazenar os detalhes da compra
        expenses[cartao].append({
            "pessoa": pessoa,
            "tipo": tipo_compra,
            "parcelas": parcelas,
            "valor": valor,
            "total": total
        })

        # Limpar os campos após adicionar a compra
        self.name_input.text = ""
        self.amount_input.text = ""
        self.installments.text = ""

    def show_report(self, instance):
        # Exibir o relatório em uma nova tela
        self.report_screen.display_report(expenses)
        self.sm.current = 'report'


if __name__ == "__main__":
    ExpenseApp().run()
