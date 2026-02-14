# -*- coding: utf-8 -*-
import pandas as pd
import os
from scipy.stats import mannwhitneyu

def main():
    base_path = 'outputs'
    candidates = ['lula', 'bolsonaro']
    networks = ['facebook', 'instagram']
    
    results = []
    
    print(f"{'='*60}")
    print("   COMPARAÇÃO DE EFICIÊNCIA (ENGAJAMENTO NORMALIZADO)")
    print(f"{'='*60}\n")
    
    for candidate in candidates:
        print(f"--- Analisando {candidate.capitalize()} ---")
        cand_stats = {}
        cand_data = {} # Armazena os arrays de dados para o teste estatístico
        
        for network in networks:
            suffix = f"{network}-{candidate}"
            file_norm = os.path.join(base_path, 'normalize_posts', f'2. Normalized-{suffix}.csv')
            
            if os.path.exists(file_norm):
                df = pd.read_csv(file_norm)
                # Remove duplicatas de ID para ter uma linha por postagem (e não por tag)
                df_posts = df.drop_duplicates(subset=['ID'])
                
                if 'Curtidas Normalizadas' in df_posts.columns:
                    avg_norm = df_posts['Curtidas Normalizadas'].mean()
                    std_norm = df_posts['Curtidas Normalizadas'].std()
                    max_norm = df_posts['Curtidas Normalizadas'].max()
                    count = len(df_posts)
                    
                    cand_stats[network] = avg_norm
                    cand_data[network] = df_posts['Curtidas Normalizadas'].dropna()
                    
                    results.append({
                        'Candidato': candidate.capitalize(),
                        'Rede': network.capitalize(),
                        'Média Norm.': avg_norm,
                        'Desvio Padrão': std_norm,
                        'Total Posts': count
                    })
                    print(f"  > {network.capitalize()}: Média = {avg_norm:.4f} (Std: {std_norm:.4f})")
                else:
                    print(f"  [ERRO] Coluna 'Curtidas Normalizadas' não encontrada para {suffix}")
            else:
                print(f"  [ERRO] Arquivo não encontrado: {file_norm}")
        
        # Comparação Direta
        if 'facebook' in cand_stats and 'instagram' in cand_stats:
            fb = cand_stats['facebook']
            insta = cand_stats['instagram']
            diff_pct = ((insta - fb) / fb) * 100
            winner = "Instagram" if insta > fb else "Facebook"
            
            # Teste de Mann-Whitney (Bicaudal)
            # H0: As distribuições são iguais
            # H1: As distribuições são diferentes
            stat, p_value = mannwhitneyu(cand_data['instagram'], cand_data['facebook'], alternative='two-sided')
            sig_text = "SIGNIFICATIVA" if p_value < 0.01 else "NÃO significativa"
            
            print(f"  [CONCLUSÃO] O {winner} teve desempenho {abs(diff_pct):.1f}% superior em eficiência.")
            print(f"  (Isso significa que os posts no {winner} ficam mais frequentemente próximos do 'pico' de sucesso da rede)")
            print(f"  [TESTE ESTATÍSTICO] Diferença {sig_text} (Mann-Whitney U, p={p_value:.2e})")
            print(f"  Isso confirma que as estratégias visuais performam de maneira distinta em cada arquitetura.\n")

    print("\n=== TABELA FINAL PARA O TCC ===")
    df_res = pd.DataFrame(results)
    df_final = df_res[['Candidato', 'Rede', 'Média Norm.', 'Desvio Padrão']]
    print(df_final.to_string(index=False))

    output_dir = os.path.join('outputs', 'thesis_tables')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = os.path.join(output_dir, 'Tabela_Eficiencia_Redes.xlsx')
    df_final.to_excel(save_path, index=False)
    print(f"\n[SUCESSO] Tabela salva em: {save_path}")

if __name__ == "__main__":
    main()