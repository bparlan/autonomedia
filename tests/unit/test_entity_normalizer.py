from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer

def test_normalization():
    normalizer = EntityNormalizer(registry_path="src/autonomedia/content/mention_registry.json")
    
    # Test valid replacement
    text = "Check out openai innovations"
    normalized = normalizer.normalize_text(text, "mastodon")
    assert "@openai@mastodon.social" in normalized
    
    # Test fallback
    text_2 = "Autonomedia is great"
    normalized_2 = normalizer.normalize_text(text_2, "linkedin")
    assert "Autonomedia" in normalized_2 # Should stay plain text, not @Autonomedia
    
    print("All tests passed!")

if __name__ == "__main__":
    test_normalization()
