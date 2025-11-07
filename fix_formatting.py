#!/usr/bin/env python3
"""
Script para corrigir problemas de formatação nos arquivos Python.
"""

import os
import re
from pathlib import Path


def fix_trailing_whitespace(content: str) -> str:
    """Remove espaços em branco no final das linhas."""
    lines = content.split('\n')
    fixed_lines = [line.rstrip() for line in lines]
    return '\n'.join(fixed_lines)


def ensure_final_newline(content: str) -> str:
    """Garante que o arquivo termina com nova linha."""
    if content and not content.endswith('\n'):
        content += '\n'
    return content


def fix_file(file_path: Path):
    """Corrige formatação de um arquivo."""
    print(f"Corrigindo {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar correções
    content = fix_trailing_whitespace(content)
    content = ensure_final_newline(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ {file_path.name} corrigido")


def main():
    """Corrige todos os arquivos Python do projeto."""
    root_dir = Path('/workspaces/meta-classificador')
    
    # Arquivos para corrigir
    files_to_fix = [
        root_dir / 'src' / 'modelos_ml.py',
        root_dir / 'src' / 'preprocessamento.py',
        root_dir / 'src' / 'meta_classificador_llm.py',
        root_dir / 'src' / 'validador_sistema.py',
        root_dir / 'src' / 'api.py',
        root_dir / 'tests' / 'test_preprocessamento.py',
        root_dir / 'tests' / 'test_modelos_ml.py',
    ]
    
    print("=" * 60)
    print("Corrigindo formatação de arquivos Python")
    print("=" * 60)
    
    for file_path in files_to_fix:
        if file_path.exists():
            fix_file(file_path)
        else:
            print(f"  ⚠ {file_path.name} não encontrado")
    
    print("\n✅ Formatação corrigida com sucesso!")


if __name__ == '__main__':
    main()
