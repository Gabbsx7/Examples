import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

# Criar Client supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL ou KEY não foi inserido nas variáveis de ambiente")

supabase: Client = create_client(url, key)

def process_risk_data():
    try:
        # Buscar dados da view
        response = supabase.table("resume_risk_dt").select(
            "user_id, risk_form_id, probabilidade, saude_segurança, meio_ambiente, comunidade, "
            "legal, reputacional, financeiro, operacional, credito, eficiencia"
        ).execute()

        # Converter para dataframe
        df = pd.DataFrame(response.data)

        print(df)

        if df.empty:
            print("Dados não encontrados")
            return

        # Colunas de mensuração de severidade
        impact_columns = [
            "saude_segurança", "meio_ambiente", "comunidade", "legal", 
            "reputacional", "financeiro", "operacional", "credito"
        ]

        # Transformar para tipo de dados númericos
        numeric_columns = impact_columns + ["probabilidade", "eficiencia"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular impacto total com base na maior severidade
        df["impacto_total"] = df[impact_columns].max(axis=1)

        # Calcular risco inerente (risco total)
        df["risco_inerente"] = df["probabilidade"] * df["impacto_total"]

        # Calcular risco residual (O que sobra após planos de mitigação)
        df["risco_residual"] = df["risco_inerente"] * (1 - df["eficiencia"])

        # Função para classificação de risco
        def classify_risk_level(risk_value):
            if risk_value <= 10:
                return "Baixo"
            elif 11 <= risk_value <= 30:
                return "Moderado"
            elif 31 <= risk_value <= 100:
                return "Alto"
            elif 101 <= risk_value <= 900:
                return "Severo"
            else:
                return "Extremo"

        # Associar nivel de risco com a coluna
        df["nivel_risco"] = df["risco_inerente"].apply(classify_risk_level)

        # Tratando valores duplicados (atualizar caso já exista)
        existing_data_response = supabase.table("risk_analytics").select("risk_form_id").execute()
        existing_ids = set(item["risk_form_id"] for item in existing_data_response.data or [])

        # Preparar dados para upsert
        rows_to_upsert = []
        for _, row in df.iterrows():
            data_to_upsert = {
                "user_id": row["user_id"],
                "risk_form_id": row["risk_form_id"],
                "risco_inerente": row["risco_inerente"],
                "risco_residual": row["risco_residual"],
                "nivel_risco": row["nivel_risco"]
            }
            rows_to_upsert.append(data_to_upsert)

        # Upsert
        for row in rows_to_upsert:
            try:
                if row["risk_form_id"] in existing_ids:
                    # Atualizar registros existentes
                    supabase.table("risk_analytics").update(row).eq("risk_form_id", row["risk_form_id"]).execute()
                else:
                    # Inserir novo registro (Caso o risk_form_id não esteja duplicado)
                    supabase.table("risk_analytics").insert(row).execute()
            except Exception as e:
                print(f"Error processing risk_form_id {row['risk_form_id']}: {e}")

        print(f"Foram processados {len(rows_to_upsert)} com sucesso")

    except Exception as e:
        print(f"Um erro ocoreu: {e}")

# Iniciar o processo
if __name__ == "__main__":
    process_risk_data()
