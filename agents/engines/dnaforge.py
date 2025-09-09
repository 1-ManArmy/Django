"""
OneLastAI Platform - DNAForge Agent Engine
Biotech and genetic analysis specialist for life sciences
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DNAForgeEngine(BaseAgentEngine):
    """
    DNAForge - Biotech Analysis Engine
    Specializes in genetic analysis, biotech applications, and life sciences
    """
    
    def __init__(self):
        super().__init__('dnaforge')
        self.biotech_domains = self.initialize_biotech_domains()
    
    def initialize_biotech_domains(self) -> Dict[str, Any]:
        """Initialize biotechnology domains and their characteristics."""
        return {
            'genomics': {
                'areas': ['dna_sequencing', 'genome_analysis', 'variant_calling', 'comparative_genomics'],
                'techniques': ['ngs', 'pcr', 'crispr', 'gwas'],
                'applications': ['disease_research', 'personalized_medicine', 'agriculture', 'evolution']
            },
            'proteomics': {
                'areas': ['protein_structure', 'function_prediction', 'interaction_networks', 'expression_analysis'],
                'techniques': ['mass_spectrometry', 'x_ray_crystallography', 'nmr', 'cryo_em'],
                'applications': ['drug_discovery', 'biomarkers', 'therapeutics', 'diagnostics']
            },
            'bioinformatics': {
                'areas': ['sequence_alignment', 'phylogenetics', 'structural_biology', 'systems_biology'],
                'techniques': ['blast', 'hmm', 'molecular_dynamics', 'network_analysis'],
                'applications': ['annotation', 'prediction', 'modeling', 'database_mining']
            },
            'synthetic_biology': {
                'areas': ['genetic_engineering', 'metabolic_engineering', 'biosynthesis', 'biodesign'],
                'techniques': ['dna_assembly', 'directed_evolution', 'metabolic_modeling', 'circuit_design'],
                'applications': ['biofuels', 'pharmaceuticals', 'materials', 'biosensors']
            },
            'clinical_genetics': {
                'areas': ['genetic_testing', 'counseling', 'rare_diseases', 'pharmacogenomics'],
                'techniques': ['karyotyping', 'fish', 'array_cgh', 'exome_sequencing'],
                'applications': ['diagnosis', 'treatment', 'prevention', 'family_planning']
            },
            'agricultural_biotech': {
                'areas': ['crop_improvement', 'pest_resistance', 'yield_optimization', 'nutrition_enhancement'],
                'techniques': ['marker_assisted_selection', 'transgenic_technology', 'gene_editing', 'breeding'],
                'applications': ['food_security', 'sustainability', 'climate_adaptation', 'nutrition']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with biotech and genetics focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'biotech_analysis'
            context['user_message'] = message
            
            # Analyze biotech requirements
            biotech_analysis = self.analyze_biotech_intent(message)
            context['biotech_analysis'] = biotech_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build biotech-focused system prompt
            biotech_prompt = self.build_biotech_prompt(biotech_analysis)
            enhanced_prompt = self.system_prompt + biotech_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            response = ai_service.chat_completion(
                messages=messages,
                **self.get_ai_parameters()
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in DNAForge engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_biotech_intent(self, message: str) -> Dict[str, Any]:
        """Analyze biotech and genetic analysis intent."""
        message_lower = message.lower()
        
        # Detect biotech domain
        domain_scores = {}
        for domain, config in self.biotech_domains.items():
            score = 0
            if domain in message_lower:
                score += 3
            
            # Check for domain-specific areas and techniques
            for area in config['areas']:
                if area.replace('_', ' ') in message_lower:
                    score += 2
            
            for technique in config['techniques']:
                if technique.replace('_', ' ') in message_lower:
                    score += 2
            
            for application in config['applications']:
                if application.replace('_', ' ') in message_lower:
                    score += 1
            
            if score > 0:
                domain_scores[domain] = score
        
        # Detect research type
        research_types = {
            'basic': any(word in message_lower for word in 
                         ['basic', 'fundamental', 'research', 'discovery']),
            'applied': any(word in message_lower for word in 
                           ['applied', 'practical', 'clinical', 'therapeutic']),
            'translational': any(word in message_lower for word in 
                                 ['translational', 'bench_to_bedside', 'clinical_trial']),
            'industrial': any(word in message_lower for word in 
                              ['industrial', 'commercial', 'manufacturing', 'production'])
        }
        
        # Detect analysis level
        levels = {
            'molecular': any(word in message_lower for word in 
                             ['molecular', 'dna', 'rna', 'protein', 'gene']),
            'cellular': any(word in message_lower for word in 
                            ['cellular', 'cell', 'culture', 'expression']),
            'organism': any(word in message_lower for word in 
                            ['organism', 'model', 'animal', 'plant']),
            'population': any(word in message_lower for word in 
                              ['population', 'epidemiological', 'cohort', 'gwas'])
        }
        
        # Detect ethical considerations
        ethics = {
            'privacy': any(word in message_lower for word in 
                           ['privacy', 'confidential', 'data_protection']),
            'consent': any(word in message_lower for word in 
                           ['consent', 'informed', 'ethics', 'approval']),
            'safety': any(word in message_lower for word in 
                          ['safety', 'biosafety', 'risk', 'containment']),
            'equity': any(word in message_lower for word in 
                          ['equity', 'access', 'fairness', 'disparity'])
        }
        
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0] \
                        if domain_scores else 'genomics'
        
        research_type = max(research_types.items(), key=lambda x: x[1])[0] \
                       if any(research_types.values()) else 'applied'
        
        analysis_level = max(levels.items(), key=lambda x: x[1])[0] \
                        if any(levels.values()) else 'molecular'
        
        ethical_considerations = [k for k, v in ethics.items() if v]
        
        return {
            'domain': primary_domain,
            'research_type': research_type,
            'analysis_level': analysis_level,
            'ethics': ethical_considerations,
            'biotech_terms': self.extract_biotech_terms(message)
        }
    
    def extract_biotech_terms(self, message: str) -> List[str]:
        """Extract biotech and genetics terms mentioned."""
        terms = [
            'dna', 'rna', 'protein', 'gene', 'genome', 'chromosome',
            'mutation', 'variant', 'allele', 'sequencing', 'pcr', 'crispr',
            'expression', 'regulation', 'pathway', 'biomarker', 'therapeutic'
        ]
        
        message_lower = message.lower()
        detected = [term for term in terms if term in message_lower]
        
        return detected[:8]  # Return up to 8 biotech terms
    
    def build_biotech_prompt(self, biotech_analysis: Dict[str, Any]) -> str:
        """Build biotech and genetics focused prompt."""
        domain = biotech_analysis['domain']
        research_type = biotech_analysis['research_type']
        level = biotech_analysis['analysis_level']
        ethics = biotech_analysis.get('ethics', [])
        terms = biotech_analysis.get('biotech_terms', [])
        
        prompt = f"\n\nBiotech Focus: {domain.title()}"
        prompt += f"\n- Research Type: {research_type.title()}"
        prompt += f"\n- Analysis Level: {level.title()}"
        
        if ethics:
            prompt += f"\n- Ethical Considerations: {', '.join(ethics)}"
        
        if terms:
            prompt += f"\n- Biotech Terms: {', '.join(terms)}"
        
        # Add domain-specific guidance
        if domain in self.biotech_domains:
            domain_config = self.biotech_domains[domain]
            prompt += f"\n- Key Areas: {', '.join([a.replace('_', ' ') for a in domain_config['areas'][:3]])}"
            prompt += f"\n- Techniques: {', '.join([t.replace('_', ' ') for t in domain_config['techniques'][:3]])}"
            prompt += f"\n- Applications: {', '.join([a.replace('_', ' ') for a in domain_config['applications'][:3]])}"
        
        research_guidance = {
            'basic': "Focus on fundamental scientific understanding, discovery, and theoretical frameworks.",
            'applied': "Focus on practical applications, problem-solving, and real-world implementation.",
            'translational': "Focus on bridging research and clinical application, moving from lab to practice.",
            'industrial': "Focus on commercial viability, scalability, and manufacturing considerations."
        }
        
        level_guidance = {
            'molecular': "Focus on molecular mechanisms, genetic sequences, and biochemical processes.",
            'cellular': "Focus on cellular functions, culture systems, and cellular-level interactions.",
            'organism': "Focus on whole organism studies, model systems, and physiological responses.",
            'population': "Focus on population-level analysis, epidemiological patterns, and public health implications."
        }
        
        prompt += f"\n\nResearch Guidance: {research_guidance.get(research_type, 'Provide comprehensive biotech analysis.')}"
        prompt += f"\nLevel Guidance: {level_guidance.get(level, 'Match analysis to appropriate biological level.')}"
        
        if ethics:
            prompt += f"\nEthical Note: Always consider {', '.join(ethics)} in biotech applications and research."
        
        return prompt