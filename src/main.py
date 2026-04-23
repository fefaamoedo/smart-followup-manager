import os
from preprocess import carregar_base
from metrics import tratar_followups
from visualize import gerar_dashboard_png
from report import gerar_relatorio_pdf


def main():
    input_file = "../data/followups.csv"
    output_dir = "../outputs"

    os.makedirs(output_dir, exist_ok=True)

    df = carregar_base(input_file)
    df_tratado = tratar_followups(df)

    caminho_csv = os.path.join(output_dir, "followup_priorizado.csv")
    df_tratado.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

    caminho_png = gerar_dashboard_png(df_tratado, output_dir)
    caminho_pdf = gerar_relatorio_pdf(df_tratado, caminho_png, output_dir)

    print("Projeto executado com sucesso.")
    print(f"CSV gerado em: {caminho_csv}")
    print(f"PNG gerado em: {caminho_png}")
    print(f"PDF gerado em: {caminho_pdf}")


if __name__ == "__main__":
    main()
