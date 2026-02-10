"""Testes unitários para name_utils."""
import pytest

from app.utils.name_utils import (
    normalize_client_name,
    sanitize_folder_name,
    build_feature_folder_name,
)


class TestNormalizeClientName:
    """Testes para normalize_client_name."""

    def test_title_case(self):
        assert normalize_client_name("CAMIL ALIMENTOS") == "Camil Alimentos"

    def test_empty_returns_sem_cliente(self):
        assert normalize_client_name("") == "Sem Cliente"
        assert normalize_client_name("   ") == "Sem Cliente"

    def test_single_word(self):
        assert normalize_client_name("cliente") == "Cliente"

    def test_invalid_chars_replaced(self):
        s = normalize_client_name("Cliente/Teste*Nome")
        assert "/" not in s
        assert "*" not in s


class TestSanitizeFolderName:
    """Testes para sanitize_folder_name."""

    def test_removes_invalid_chars(self):
        assert "\\" not in sanitize_folder_name("a\\b/c:d")
        assert "/" not in sanitize_folder_name("a/b")

    def test_empty_returns_empty(self):
        assert sanitize_folder_name("") == ""

    def test_truncates_long(self):
        long_title = "A" * 300
        result = sanitize_folder_name(long_title, max_length=100)
        assert len(result) <= 100
        assert result.endswith("...")

    def test_collapses_spaces(self):
        result = sanitize_folder_name("  a   b   ")
        assert "  " not in result.strip() or result == "a b"


class TestBuildFeatureFolderName:
    """Testes para build_feature_folder_name."""

    def test_full(self):
        name = build_feature_folder_name(12345, "001", "Implementar login")
        assert "12345" in name
        assert "001" in name
        assert "Implementar login" in name or "Implementar" in name

    def test_empty_numero_proposta_uses_placeholder(self):
        name = build_feature_folder_name(100, None, "Título")
        assert "N/A" in name
        assert "100" in name

    def test_empty_title_uses_sem_titulo(self):
        name = build_feature_folder_name(1, "P1", "")
        assert "Sem título" in name
        assert "1" in name
