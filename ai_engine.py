from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from groq import Groq

# -------------------------------------------------------------
# Pydantic Schemas for Structured JSON Output validation
# -------------------------------------------------------------

class Competitor(BaseModel):
    name: str = Field(description="Name of the competitor")
    description: str = Field(description="Short description of who they are and what they offer")
    strengths: str = Field(description="Key strengths/advantages of this competitor")
    weaknesses: str = Field(description="Key weaknesses/gaps of this competitor")
    positioning: str = Field(description="How this competitor positions themselves (e.g. low-cost, premium, specific niche)")

class Persona(BaseModel):
    name: str = Field(description="A catchy user persona name (e.g. Founder Frank, Student Sarah)")
    role: str = Field(description="Professional role or demographic description")
    goals: str = Field(description="Primary goals or objectives of this persona")
    pain_points: str = Field(description="Main challenges, pain points, or frustrations they face")
    buying_motivation: str = Field(description="What motivates this persona to purchase or adopt our solution")

class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(description="3-5 internal strengths of the proposed startup")
    weaknesses: List[str] = Field(description="3-5 internal weaknesses or limitations")
    opportunities: List[str] = Field(description="3-5 external opportunities in the market")
    threats: List[str] = Field(description="3-5 external threats or risks")

class GTMStrategy(BaseModel):
    icp: str = Field(description="Detailed description of the Ideal Customer Profile")
    positioning: str = Field(description="Value proposition and brand positioning statement")
    pricing_recommendation: str = Field(description="Recommended pricing model (e.g., Freemium, tiered SaaS, one-time fee) with suggested price ranges")
    marketing_channels: List[str] = Field(description="List of 3-4 recommended marketing channels (specifically cover how they apply to LinkedIn, SEO, Communities, or Partnerships)")
    sales_strategy: str = Field(description="Recommended sales methodology (e.g. self-serve, direct outbound sales, content inbound)")
    launch_roadmap_30_day: List[str] = Field(description="A sequential weekly plan (e.g. Week 1: setup landing page, Week 2: soft launch, etc.)")

class InvestorReadiness(BaseModel):
    market_attractiveness_score: int = Field(description="Score between 0 and 100")
    market_attractiveness_rationale: str = Field(description="Brief rationale explaining the market attractiveness score")
    business_viability_score: int = Field(description="Score between 0 and 100")
    business_viability_rationale: str = Field(description="Brief rationale explaining the business viability score")
    scalability_score: int = Field(description="Score between 0 and 100")
    scalability_rationale: str = Field(description="Brief rationale explaining the scalability score")
    funding_readiness_score: int = Field(description="Score between 0 and 100")
    funding_readiness_rationale: str = Field(description="Brief rationale explaining the funding readiness score")

class GTMReport(BaseModel):
    validation_score: int = Field(description="Overall validation score between 0 and 100 based on solution feasibility and market fit")
    opportunity_score: int = Field(description="Overall opportunity score between 0 and 100 based on market potential")
    risk_score: int = Field(description="Overall risk score between 0 and 100 based on competitor density and execution risk")
    summary: str = Field(description="A concise executive summary validating the idea (1-2 paragraphs)")
    
    industry_overview: str = Field(description="A high-level overview of the current industry landscape")
    market_trends: List[str] = Field(description="3-4 key trends currently shaping this market")
    emerging_opportunities: List[str] = Field(description="3-4 emerging opportunities within this industry")
    key_challenges: List[str] = Field(description="3-4 major challenges facing the industry")
    
    direct_competitors: List[Competitor] = Field(description="List of exactly 2-3 direct competitors")
    indirect_competitors: List[Competitor] = Field(description="List of exactly 2-3 indirect competitors")
    
    personas: List[Persona] = Field(description="List of exactly 3 distinct customer personas")
    
    market_gap_underserved_segments: str = Field(description="Description of customer segments underserved by competitors")
    market_gap_missing_features: str = Field(description="Description of features or capabilities missing from competitor products")
    market_gap_product_opportunities: str = Field(description="Specific white space product opportunities the startup should build")
    market_gap_opportunity_score: int = Field(description="Score between 0 and 100 indicating the extent of the white space gap")
    
    swot: SWOTAnalysis = Field(description="A complete SWOT analysis")
    
    gtm: GTMStrategy = Field(description="Go-to-market strategy elements")
    
    investor_readiness: InvestorReadiness = Field(description="Investor readiness score card")


def clean_json_response(content: str) -> str:
    """Cleans up markdown code blocks if the model wrapped the JSON in them."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def generate_gtm_report(
    name: str,
    industry: str,
    problem: str,
    target_customer: str,
    country: str,
    api_key: str,
    model: str = "llama-3.3-70b-versatile"
) -> GTMReport:
    """
    Calls Groq API in JSON Mode to perform market research and GTM planning,
    and returns a structured GTMReport Pydantic object.
    """
    if not api_key:
        raise ValueError("Groq API Key is required. Please set it in your environment or sidebar.")

    client = Groq(api_key=api_key)

    # Convert the Pydantic schema to JSON schema string to give to Llama
    schema_str = json.dumps(GTMReport.model_json_schema(), indent=2)

    system_prompt = f"""You are an elite Venture Capital analyst and GTM strategist.
Your task is to analyze the proposed startup idea and return a complete GTM research and validation report.

You MUST respond with a JSON object that adheres EXACTLY to the following JSON schema:
{schema_str}

Ensure your response is valid JSON. Do not include markdown code blocks or wrapping (like ```json), just return the raw JSON string. Do not omit any fields. Do not add any text before or after the JSON. Do not use any emojis or icons in your response.
"""

    user_prompt = f"""Analyze this startup idea:
Startup Name: {name}
Industry: {industry}
Problem Statement: {problem}
Target Customer: {target_customer}
Country/Region: {country}

Provide:
1. Validation, Opportunity, and Risk Scores (0-100) and a comprehensive summary.
2. Market Research (Industry overview, trends, opportunities, challenges).
3. Competitor Intelligence (Direct and Indirect, with Description, Strengths, Weaknesses, Positioning).
4. Customer Personas (3 distinct profiles).
5. Market Gap Finder (underserved segments, missing features, product white space, and Gap Opportunity Score).
6. SWOT Analysis.
7. Go-To-Market Strategy (ICP, Positioning, Pricing, Marketing Channels like LinkedIn, SEO, Communities, Partnerships, Sales Strategy, and a 30-Day Launch Roadmap).
8. Investor Readiness Assessment (Attractiveness, Viability, Scalability, Funding scores and rationales).
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2, # Lower temperature for structured accuracy
            max_tokens=4000
        )
        
        raw_content = response.choices[0].message.content
        cleaned_content = clean_json_response(raw_content)
        
        # Parse the JSON directly into our Pydantic model
        report_data = GTMReport.model_validate_json(cleaned_content)
        return report_data
        
    except Exception as e:
        raise Exception(f"Failed to generate GTM report: {str(e)}")
