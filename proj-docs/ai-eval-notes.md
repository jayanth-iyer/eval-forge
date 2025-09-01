# AI Evaluation Practical Notes

## 1. How do I test applications when the outputs are stochastic and require subjective judgements?

### **The Challenge**
Stochastic AI outputs vary between runs, making traditional deterministic testing approaches ineffective. Subjective quality assessment adds another layer of complexity.

### **Solutions & Strategies**

#### **Statistical Sampling Approach**
- **Multiple Runs**: Test each input 5-10 times to capture variance
- **Aggregate Metrics**: Use mean, median, and confidence intervals
- **Variance Tracking**: Monitor consistency across runs
```python
# Example: Test prompt 10 times, measure variance
results = [run_model(prompt) for _ in range(10)]
avg_score = np.mean([score(r) for r in results])
variance = np.var([score(r) for r in results])
```

#### **Human-in-the-Loop Evaluation**
- **Crowd Evaluation**: Use platforms like Scale AI, Surge, or internal reviewers
- **Expert Review**: Domain experts for specialized content
- **Comparative Ranking**: A/B testing between model versions
- **Rubric-Based Scoring**: Define clear criteria (1-5 scale for relevance, accuracy, etc.)

#### **LLM-as-Judge Pattern**
- **GPT-4 as Evaluator**: Use stronger models to judge weaker ones
- **Multi-Aspect Scoring**: Rate different dimensions separately
- **Chain-of-Thought Evaluation**: Ask the judge to explain its reasoning
```python
evaluation_prompt = f"""
Rate this response on a scale of 1-5 for:
- Accuracy: How factually correct is it?
- Relevance: How well does it answer the question?
- Clarity: How easy is it to understand?

Response: {model_output}
Provide scores and brief justification.
"""
```

#### **Proxy Metrics**
- **Length Consistency**: Track output length patterns
- **Keyword Presence**: Check for required terms or concepts
- **Format Compliance**: Ensure outputs follow expected structure
- **Sentiment Analysis**: Monitor emotional tone consistency

## 2. If I change the prompt, how do I know I am not breaking something else?

### **Regression Testing for Prompts**

#### **Golden Dataset Approach**
- **Curate Test Cases**: Build a comprehensive set of representative inputs
- **Baseline Performance**: Record current model performance on all test cases
- **Change Detection**: Compare new prompt performance against baseline
- **Regression Threshold**: Define acceptable performance degradation (e.g., <5% drop)

#### **Prompt Versioning System**
```python
# Example structure
prompt_versions = {
    "v1.0": "Original prompt...",
    "v1.1": "Modified prompt with better instructions...",
    "v1.2": "Further refined prompt..."
}

def test_prompt_regression(old_version, new_version, test_cases):
    old_results = [run_model(old_version, case) for case in test_cases]
    new_results = [run_model(new_version, case) for case in test_cases]
    return compare_performance(old_results, new_results)
```

#### **Multi-Dimensional Testing**
- **Core Functionality**: Test primary use case thoroughly
- **Edge Cases**: Verify handling of unusual inputs
- **Cross-Domain**: Test across different content types/domains
- **Error Handling**: Ensure graceful failure modes remain intact

#### **Canary Deployment**
- **Gradual Rollout**: Test new prompt on small user subset first
- **A/B Testing**: Run old and new prompts in parallel
- **Monitoring**: Track key metrics during transition
- **Rollback Plan**: Quick revert mechanism if issues arise

## 3. Where should I focus my engineering efforts? Do I need to test everything?

### **Risk-Based Testing Prioritization**

#### **High-Priority Areas**
1. **Core User Journeys**: Test the 80% use cases thoroughly
2. **Safety-Critical Outputs**: Anything that could cause harm or misinformation
3. **Business-Critical Features**: Revenue-impacting functionality
4. **User-Facing Outputs**: Direct customer interactions
5. **Regulatory Requirements**: Compliance-mandated testing

#### **Testing Pyramid for AI**
```
    /\     Manual Expert Review (5%)
   /  \    Human Evaluation (15%)
  /____\   Automated LLM Evaluation (30%)
 /______\  Unit Tests & Metrics (50%)
```

#### **Focus Areas by Development Stage**
- **MVP/Early Stage**: Focus on core functionality and basic safety
- **Growth Stage**: Add comprehensive regression testing and edge cases
- **Scale Stage**: Implement automated evaluation pipelines and monitoring

#### **Resource Allocation Strategy**
- **20% on Core Functionality**: Ensure primary features work reliably
- **30% on Safety & Compliance**: Prevent harmful outputs
- **25% on Regression Testing**: Maintain existing quality
- **15% on Edge Cases**: Handle unusual scenarios
- **10% on Performance Optimization**: Speed and efficiency

## 4. What if I have no data or customers? Where do I start?

### **Bootstrap Evaluation Strategy**

#### **Synthetic Data Generation**
- **Create Personas**: Define 3-5 user archetypes
- **Generate Scenarios**: Create realistic use cases for each persona
- **Vary Complexity**: Include simple, medium, and complex examples
```python
personas = [
    {"name": "Beginner", "context": "New to the domain", "needs": "Simple explanations"},
    {"name": "Expert", "context": "Domain expert", "needs": "Detailed technical info"},
    {"name": "Casual User", "context": "Occasional use", "needs": "Quick answers"}
]
```

#### **Domain Expert Consultation**
- **Subject Matter Experts**: Consult 2-3 domain experts
- **Academic Sources**: Use research papers and textbooks
- **Industry Standards**: Follow established best practices
- **Competitive Analysis**: Study how similar products handle evaluation

#### **Minimum Viable Evaluation (MVE)**
1. **10-20 Test Cases**: Cover main functionality
2. **3 Quality Dimensions**: Accuracy, relevance, safety
3. **Simple Scoring**: 1-5 scale or pass/fail
4. **Weekly Reviews**: Regular evaluation cycles
5. **Iteration Based**: Improve based on findings

#### **Community & Open Source**
- **Public Datasets**: Use existing evaluation datasets in your domain
- **Benchmark Suites**: Leverage standard AI benchmarks
- **Open Source Tools**: Start with free evaluation frameworks
- **Academic Partnerships**: Collaborate with researchers

## 5. What metrics should I track? What tools should I use? Which models are the best?

### **Essential Metrics Framework**

#### **Quality Metrics**
- **Accuracy**: Factual correctness (0-100%)
- **Relevance**: How well output matches intent (1-5 scale)
- **Completeness**: Coverage of required information (0-100%)
- **Coherence**: Logical flow and consistency (1-5 scale)
- **Safety**: Absence of harmful content (pass/fail)

#### **Performance Metrics**
- **Latency**: Response time (milliseconds)
- **Throughput**: Requests per second
- **Cost**: $ per 1K tokens/requests
- **Reliability**: Uptime and error rates
- **Consistency**: Variance across multiple runs

#### **Business Metrics**
- **User Satisfaction**: CSAT scores, thumbs up/down
- **Task Completion**: Success rate for user goals
- **Engagement**: Session length, return usage
- **Conversion**: Business objective achievement

### **Recommended Tools**

#### **Evaluation Frameworks**
- **LangSmith**: Comprehensive LLM evaluation and monitoring
- **Weights & Biases**: ML experiment tracking with LLM support
- **Phoenix**: Open-source LLM observability
- **Braintrust**: AI evaluation and monitoring platform
- **Custom Solutions**: Build on your React/FastAPI stack

#### **Testing Tools**
- **Pytest**: Unit testing framework
- **Locust**: Load testing for AI APIs
- **Great Expectations**: Data quality testing
- **MLflow**: Model versioning and tracking

#### **Monitoring & Observability**
- **LangFuse**: Open-source LLM tracing
- **Helicone**: LLM observability and caching
- **DataDog**: Application performance monitoring
- **Grafana**: Custom dashboards and alerting

### **Model Recommendations**

#### **For Evaluation (LLM-as-Judge)**
1. **GPT-4**: Best overall evaluation quality
2. **Claude-3**: Strong reasoning and safety awareness
3. **GPT-3.5-Turbo**: Cost-effective for basic evaluation
4. **Local Models**: Llama-3.1-70B via Ollama for privacy

#### **For Production (Based on Use Case)**
- **General Purpose**: GPT-4, Claude-3, Gemini Pro
- **Code Generation**: GPT-4, Claude-3, CodeLlama
- **Privacy-First**: Llama-3.1, Mistral (via Ollama)
- **Cost-Sensitive**: GPT-3.5-Turbo, Gemini Flash
- **Specialized**: Fine-tuned models for domain-specific tasks

## 6. Can I automate testing and evaluation? If so, how do I trust it?

### **Automation Strategy**

#### **What to Automate**
- **Regression Testing**: Automated runs on prompt changes
- **Performance Monitoring**: Latency, throughput, error rates
- **Basic Quality Checks**: Format validation, safety filters
- **Comparative Analysis**: A/B testing between model versions
- **Continuous Integration**: Evaluation in deployment pipeline

#### **Automation Architecture**
```python
# Example CI/CD pipeline integration
def automated_evaluation_pipeline():
    # 1. Load test cases
    test_cases = load_golden_dataset()
    
    # 2. Run model on all cases
    results = batch_evaluate(model, test_cases)
    
    # 3. Compute metrics
    metrics = calculate_metrics(results)
    
    # 4. Compare against baseline
    regression_check = compare_to_baseline(metrics)
    
    # 5. Generate report
    report = create_evaluation_report(metrics, regression_check)
    
    # 6. Alert if issues found
    if regression_check.failed:
        send_alert(report)
    
    return report
```

### **Building Trust in Automation**

#### **Validation Strategies**
- **Human Validation**: Regularly verify automated scores against human judgment
- **Inter-Rater Reliability**: Measure agreement between automated and human evaluators
- **Confidence Intervals**: Report uncertainty in automated scores
- **Spot Checks**: Random manual review of automated evaluations

#### **Multi-Layer Validation**
1. **Automated Screening**: Fast, broad coverage
2. **LLM-as-Judge**: More nuanced evaluation
3. **Human Review**: Final validation for critical cases
4. **Expert Audit**: Periodic deep review by domain experts

#### **Trust Metrics**
- **Correlation with Human Scores**: r > 0.8 indicates good alignment
- **False Positive Rate**: How often automation flags good outputs as bad
- **False Negative Rate**: How often automation misses actual problems
- **Calibration**: How well confidence scores match actual accuracy

#### **Continuous Improvement**
- **Feedback Loops**: Use human corrections to improve automation
- **Regular Recalibration**: Update evaluation criteria based on new data
- **A/B Testing**: Compare different automated evaluation approaches
- **Version Control**: Track changes to evaluation logic

### **Implementation Roadmap**

#### **Phase 1: Foundation (Weeks 1-2)**
- Set up basic automated testing
- Create golden dataset
- Implement core metrics

#### **Phase 2: Enhancement (Weeks 3-4)**
- Add LLM-as-judge evaluation
- Build comparison framework
- Create alerting system

#### **Phase 3: Optimization (Weeks 5-6)**
- Validate automation accuracy
- Optimize for speed and cost
- Add advanced analytics

#### **Phase 4: Scale (Ongoing)**
- Continuous monitoring
- Regular human validation
- Iterative improvement

---

## Key Takeaways

1. **Start Simple**: Begin with basic metrics and manual evaluation, then automate gradually
2. **Focus on Impact**: Prioritize testing based on user impact and business risk
3. **Embrace Uncertainty**: Use statistical approaches to handle stochastic outputs
4. **Build Incrementally**: Develop evaluation capabilities alongside your product
5. **Validate Automation**: Always verify that automated evaluation aligns with human judgment
6. **Iterate Continuously**: Evaluation is an ongoing process, not a one-time setup

Remember: Perfect evaluation is impossible, but systematic evaluation is essential for building reliable AI applications.
