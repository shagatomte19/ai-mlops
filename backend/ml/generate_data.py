"""
Enhanced Synthetic Data Generator for Sentiment Analysis.
Generates 5000+ diverse training samples with positive, negative, and neutral sentiments.
"""
import pandas as pd
import random
import re
from typing import List, Tuple
from datetime import datetime
import os


class DataGenerator:
    """Advanced data generator with diverse templates and augmentation."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.setup_templates()
        self.setup_vocabulary()
    
    def setup_vocabulary(self):
        """Setup diverse vocabulary for template filling."""
        self.nouns = [
            # Products
            "product", "item", "purchase", "order", "package",
            # Services  
            "service", "support", "experience", "delivery", "shipping",
            # Tech
            "app", "software", "interface", "platform", "system",
            # Quality
            "quality", "performance", "design", "features", "functionality",
            # Business
            "company", "team", "staff", "customer service", "response",
        ]
        
        self.positive_adjectives = [
            "amazing", "excellent", "fantastic", "wonderful", "outstanding",
            "superb", "brilliant", "incredible", "perfect", "exceptional",
            "remarkable", "impressive", "delightful", "terrific", "marvelous",
            "stellar", "phenomenal", "magnificent", "splendid", "top-notch",
        ]
        
        self.negative_adjectives = [
            "terrible", "horrible", "awful", "dreadful", "disappointing",
            "poor", "bad", "worst", "pathetic", "useless",
            "frustrating", "annoying", "unacceptable", "abysmal", "atrocious",
            "mediocre", "subpar", "inferior", "defective", "broken",
        ]
        
        self.positive_adverbs = [
            "absolutely", "incredibly", "extremely", "truly", "genuinely",
            "remarkably", "exceptionally", "thoroughly", "completely", "totally",
        ]
        
        self.negative_adverbs = [
            "completely", "absolutely", "totally", "utterly", "extremely",
            "incredibly", "terribly", "horribly", "deeply", "seriously",
        ]
        
        self.positive_verbs = [
            "love", "adore", "appreciate", "enjoy", "recommend",
            "praise", "cherish", "treasure", "value", "admire",
        ]
        
        self.negative_verbs = [
            "hate", "dislike", "regret", "despise", "avoid",
            "detest", "loathe", "resent", "condemn", "reject",
        ]
    
    def setup_templates(self):
        """Setup diverse sentence templates for each sentiment."""
        
        # ============ POSITIVE TEMPLATES (60+) ============
        self.positive_templates = [
            # Simple praise
            "I love this {noun}!",
            "This {noun} is amazing!",
            "Best {noun} I've ever had!",
            "Absolutely {adjective} {noun}!",
            "The {noun} is {adverb} {adjective}.",
            "{adjective} {noun}, highly recommend!",
            "Five stars for this {noun}!",
            "Can't recommend this {noun} enough!",
            "So happy with this {noun}!",
            "This {noun} exceeded my expectations.",
            
            # Detailed positive
            "The {noun} is {adverb} {adjective} and works perfectly.",
            "I'm {adverb} impressed with the {noun}.",
            "This is exactly what I was looking for in a {noun}.",
            "The {noun} has made my life so much easier.",
            "Outstanding {noun} with {adjective} features.",
            "Never been happier with a {noun} purchase.",
            "The {noun} quality is beyond {adjective}.",
            "Worth every penny for this {adjective} {noun}!",
            "Exceeded all my expectations for this {noun}.",
            "Hands down the best {noun} on the market.",
            
            # Recommendation focused
            "Would definitely recommend this {noun} to everyone.",
            "Already told all my friends about this {adjective} {noun}.",
            "If you're looking for a {noun}, this is it!",
            "This {noun} is a game changer!",
            "A must-have {noun} for anyone serious about quality.",
            "The {noun} speaks for itself - {adverb} {adjective}!",
            "Don't hesitate, this {noun} is worth it!",
            "Best decision I made was buying this {noun}.",
            "This {noun} has changed how I think about quality.",
            "The {noun} is simply {adjective} in every way.",
            
            # Specific aspects
            "The customer support for this {noun} was {adjective}.",
            "Fast shipping and the {noun} was {adjective}!",
            "Great value for money - {adjective} {noun}!",
            "The design of this {noun} is {adverb} {adjective}.",
            "Easy to use and the {noun} works {adverb} well.",
            "Packaging was perfect and {noun} arrived in {adjective} condition.",
            "The features of this {noun} are {adjective}!",
            "Setup was easy and the {noun} is {adjective}.",
            "Really impressed with the {noun} performance.",
            "The {noun} quality is {adverb} better than expected.",
            
            # Emotional expressions
            "So grateful I found this {adjective} {noun}!",
            "This {noun} brings me so much joy!",
            "Couldn't be happier with my {noun} purchase!",
            "This {noun} made my day {adverb} {adjective}!",
            "I'm in love with this {adjective} {noun}!",
            "This {noun} is a blessing - {adverb} {adjective}!",
            "My heart is full thanks to this {noun}!",
            "Tears of joy with this {adjective} {noun}!",
            "Finally found the perfect {noun}!",
            "This {noun} is everything I hoped for!",
            
            # Professional tone
            "Highly professional {noun} with {adjective} results.",
            "The {noun} meets and exceeds industry standards.",
            "Exceptional {noun} that delivers on its promises.",
            "Top-tier {noun} with {adjective} craftsmanship.",
            "Premium {noun} worth the investment.",
            "The {noun} demonstrates {adjective} attention to detail.",
            "A benchmark {noun} for quality and performance.",
            "The {noun} sets a new standard in the industry.",
            "Impeccable {noun} from a trusted source.",
            "{adjective} {noun} backed by excellent support.",
        ]
        
        # ============ NEGATIVE TEMPLATES (60+) ============
        self.negative_templates = [
            # Simple complaints
            "I hate this {noun}.",
            "This {noun} is terrible.",
            "Worst {noun} I've ever bought.",
            "{adjective} {noun}, do not buy!",
            "The {noun} is {adverb} {adjective}.",
            "Complete waste of money on this {noun}.",
            "One star is too generous for this {noun}.",
            "Avoid this {noun} at all costs!",
            "So disappointed with this {noun}.",
            "This {noun} failed to meet basic expectations.",
            
            # Detailed negative
            "The {noun} is {adverb} {adjective} and doesn't work.",
            "I'm {adverb} disappointed with the {noun}.",
            "This is nothing like what I expected from this {noun}.",
            "The {noun} has made my life more difficult.",
            "{adjective} {noun} with broken features.",
            "Never been more frustrated with a {noun}.",
            "The {noun} quality is {adverb} {adjective}.",
            "Not worth a single penny for this {adjective} {noun}!",
            "Failed all my expectations for this {noun}.",
            "Hands down the worst {noun} on the market.",
            
            # Warning focused
            "Would never recommend this {noun} to anyone.",
            "Already warned all my friends about this {adjective} {noun}.",
            "If you're looking for a {noun}, avoid this one!",
            "This {noun} is a disaster!",
            "A waste of time and money for anyone considering this {noun}.",
            "The {noun} is a scam - {adverb} {adjective}!",
            "Don't make my mistake with this {noun}.",
            "Worst decision I made was buying this {noun}.",
            "This {noun} ruined my experience completely.",
            "The {noun} is {adverb} {adjective} in every way.",
            
            # Specific issues
            "The customer support for this {noun} was {adjective}.",
            "Slow shipping and the {noun} was {adjective}!",
            "Terrible value for money - {adjective} {noun}!",
            "The design of this {noun} is {adverb} {adjective}.",
            "Difficult to use and the {noun} works {adverb} badly.",
            "Packaging was damaged and {noun} arrived in {adjective} condition.",
            "The features of this {noun} are {adjective}!",
            "Setup was a nightmare and the {noun} is {adjective}.",
            "Really disappointed with the {noun} performance.",
            "The {noun} quality is {adverb} worse than expected.",
            
            # Emotional expressions
            "So upset I wasted money on this {adjective} {noun}!",
            "This {noun} brings me so much frustration!",
            "Couldn't be more disappointed with my {noun} purchase!",
            "This {noun} ruined my day - {adverb} {adjective}!",
            "I'm fed up with this {adjective} {noun}!",
            "This {noun} is a curse - {adverb} {adjective}!",
            "My patience is gone thanks to this {noun}!",
            "Tears of frustration with this {adjective} {noun}!",
            "Why did I buy this terrible {noun}?",
            "This {noun} is nothing I hoped for!",
            
            # Technical issues
            "The {noun} broke after one use.",
            "Defective {noun} with {adjective} build quality.",
            "The {noun} stopped working immediately.",
            "Constant problems with this {adjective} {noun}.",
            "The {noun} is unreliable and {adjective}.",
            "Multiple issues with this {noun} since day one.",
            "The {noun} is poorly made and {adjective}.",
            "Had to return the {noun} - {adverb} {adjective}.",
            "The {noun} doesn't function as advertised.",
            "{adjective} {noun} that falls apart easily.",
        ]
        
        # ============ NEUTRAL TEMPLATES (30+) ============
        self.neutral_templates = [
            # Mixed feelings
            "The {noun} is okay, nothing special.",
            "It's an average {noun}, has pros and cons.",
            "The {noun} works as expected, nothing more.",
            "Neither impressed nor disappointed with this {noun}.",
            "The {noun} is decent for the price.",
            "Mixed feelings about this {noun}.",
            "The {noun} is fine, but could be better.",
            "Not sure how I feel about this {noun}.",
            "The {noun} met basic expectations only.",
            "It's a standard {noun}, nothing remarkable.",
            
            # Balanced reviews
            "The {noun} has good points and bad points.",
            "Some features of the {noun} are good, others not so much.",
            "The {noun} is functional but uninspiring.",
            "Expected more from this {noun}, but it's not bad.",
            "The {noun} does the job, nothing fancy.",
            "Adequate {noun} for basic needs.",
            "The {noun} is what you'd expect at this price.",
            "Fair {noun}, wouldn't necessarily buy again.",
            "The {noun} is satisfactory overall.",
            "Middle of the road {noun}, average in every way.",
            
            # Objective observations
            "The {noun} arrived as described.",
            "Standard {noun} with typical features.",
            "The {noun} functions as intended.",
            "Received the {noun} on time.",
            "The {noun} matches the description.",
            "Typical {noun} performance.",
            "The {noun} is comparable to others.",
            "Nothing unusual about this {noun}.",
            "The {noun} is ordinary.",
            "Just another {noun} in the market.",
        ]
    
    def fill_template(self, template: str, sentiment: str) -> str:
        """Fill template placeholders with appropriate vocabulary."""
        result = template
        
        # Choose adjectives/adverbs based on sentiment
        if sentiment == "positive":
            adjectives = self.positive_adjectives
            adverbs = self.positive_adverbs
            verbs = self.positive_verbs
        elif sentiment == "negative":
            adjectives = self.negative_adjectives
            adverbs = self.negative_adverbs
            verbs = self.negative_verbs
        else:
            # Neutral uses random mix
            adjectives = self.positive_adjectives + self.negative_adjectives
            adverbs = self.positive_adverbs + self.negative_adverbs
            verbs = self.positive_verbs + self.negative_verbs
        
        # Replace placeholders
        result = result.replace("{noun}", random.choice(self.nouns))
        result = result.replace("{adjective}", random.choice(adjectives))
        result = result.replace("{adverb}", random.choice(adverbs))
        result = result.replace("{verb}", random.choice(verbs))
        
        return result
    
    def augment_text(self, text: str) -> str:
        """Apply text augmentation for variety."""
        augmentations = [
            lambda t: t,  # Original
            lambda t: t.lower(),  # Lowercase
            lambda t: t + " Overall satisfied." if random.random() > 0.5 else t,
            lambda t: t.replace("!", ".") if random.random() > 0.5 else t,
            lambda t: t.replace(".", "!") if random.random() > 0.7 else t,
            lambda t: "Honestly, " + t[0].lower() + t[1:] if random.random() > 0.8 else t,
            lambda t: "To be fair, " + t[0].lower() + t[1:] if random.random() > 0.85 else t,
        ]
        
        return random.choice(augmentations)(text)
    
    def generate_samples(
        self, 
        positive_count: int = 2500,
        negative_count: int = 2000,
        neutral_count: int = 500
    ) -> pd.DataFrame:
        """Generate training samples with specified distribution."""
        data = []
        
        # Generate positive samples
        print(f"Generating {positive_count} positive samples...")
        for _ in range(positive_count):
            template = random.choice(self.positive_templates)
            text = self.fill_template(template, "positive")
            text = self.augment_text(text)
            data.append({"text": text, "sentiment": 1})
        
        # Generate negative samples
        print(f"Generating {negative_count} negative samples...")
        for _ in range(negative_count):
            template = random.choice(self.negative_templates)
            text = self.fill_template(template, "negative")
            text = self.augment_text(text)
            data.append({"text": text, "sentiment": 0})
        
        # Generate neutral samples (labeled as positive for binary, but low confidence)
        print(f"Generating {neutral_count} neutral samples...")
        for _ in range(neutral_count):
            template = random.choice(self.neutral_templates)
            text = self.fill_template(template, "neutral")
            text = self.augment_text(text)
            # Neutral samples are labeled based on slight lean
            sentiment = random.choice([0, 1])  # Random for binary classification
            data.append({"text": text, "sentiment": sentiment})
        
        # Shuffle and create DataFrame
        random.shuffle(data)
        df = pd.DataFrame(data)
        
        print(f"Generated {len(df)} total samples")
        return df


def generate_training_data(output_path: str = "ml/data/sentiment_dataset_v2.csv"):
    """Generate and save training dataset."""
    generator = DataGenerator(seed=42)
    
    df = generator.generate_samples(
        positive_count=2500,
        negative_count=2000,
        neutral_count=500
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Saved dataset to {output_path}")
    
    # Print statistics
    print("\nDataset Statistics:")
    print(f"  Total samples: {len(df)}")
    print(f"  Positive (1): {len(df[df['sentiment'] == 1])}")
    print(f"  Negative (0): {len(df[df['sentiment'] == 0])}")
    
    return df


if __name__ == "__main__":
    generate_training_data()
