{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RAG System Evaluation\n",
    "\n",
    "This notebook demonstrates how to evaluate the RAG system using RAGAS metrics."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "sys.path.append('..')\n",
    "\n",
    "from app.evaluation.ragas_eval import RAGEvaluator\n",
    "from app.rag.pipeline import RAGPipeline\n",
    "import json"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Prepare Test Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create sample QA pairs\n",
    "qa_pairs = [\n",
    "    {\n",
    "        'question': 'What is artificial intelligence?',\n",
    "        'answer': 'Artificial intelligence is the simulation of human intelligence in machines.',\n",
    "        'context': 'AI is the simulation of human intelligence in machines that are programmed to think and learn.'\n",
    "    },\n",
    "    {\n",
    "        'question': 'What is machine learning?',\n",
    "        'answer': 'Machine learning is a subset of AI that enables systems to learn and improve from experience.',\n",
    "        'context': 'Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.'\n",
    "    }\n",
    "]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Evaluate System"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Initialize evaluator\n",
    "evaluator = RAGEvaluator()\n",
    "\n",
    "# Evaluate\n",
    "results = evaluator.evaluate_qa_pairs(qa_pairs)\n",
    "\n",
    "# Display results\n",
    "for metric, score in results.items():\n",
    "    print(f\"{metric}: {score:.4f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Generate Report"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Generate report\n",
    "report = evaluator.generate_report(results, output_path='evaluation_report.txt')\n",
    "print(report)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Visualize Results"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "\n",
    "metrics = list(results.keys())\n",
    "scores = list(results.values())\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "plt.bar(metrics, scores, color='skyblue')\n",
    "plt.title('RAG System Evaluation Metrics')\n",
    "plt.xlabel('Metrics')\n",
    "plt.ylabel('Score')\n",
    "plt.ylim(0, 1)\n",
    "plt.xticks(rotation=45, ha='right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}