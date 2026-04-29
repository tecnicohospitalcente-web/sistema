import pandas as pd
from conexao import supabase

# =========================
# 🔒 EXECUÇÃO SEGURA
# =========================
def executar(query_func):
    try:
        res = query_func()
        if not res or not hasattr(res, "data"):
            return []
        return res.data
    except Exception as e:
        print("Erro banco:", e)
        return []


# =========================
# 📥 SELECT → LISTA
# =========================
def select(tabela, filtros=None, ordem=None):
    def run():
        q = supabase.table(tabela).select("*")

        if filtros:
            for campo, valor in filtros.items():
                q = q.eq(campo, valor)

        if ordem:
            q = q.order(ordem, desc=True)

        return q.execute()

    return executar(run)


# =========================
# 📊 SELECT → DATAFRAME
# =========================
def select_df(tabela, filtros=None, ordem=None):
    dados = select(tabela, filtros, ordem)
    return pd.DataFrame(dados)


# =========================
# 💾 INSERT
# =========================
def insert(tabela, dados):
    try:
        supabase.table(tabela).insert(dados).execute()
        return True
    except Exception as e:
        print("Erro insert:", e)
        return False


# =========================
# ✏️ UPDATE
# =========================
def update(tabela, dados, filtros):
    try:
        q = supabase.table(tabela).update(dados)

        for campo, valor in filtros.items():
            q = q.eq(campo, valor)

        q.execute()
        return True
    except Exception as e:
        print("Erro update:", e)
        return False


# =========================
# 🗑️ DELETE
# =========================
def delete(tabela, filtros):
    try:
        q = supabase.table(tabela).delete()

        for campo, valor in filtros.items():
            q = q.eq(campo, valor)

        q.execute()
        return True
    except Exception as e:
        print("Erro delete:", e)
        return False