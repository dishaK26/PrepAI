import os
import json
import requests
from google import genai
from google.genai import types

os.environ["GEMINI_API_KEY"] = ""
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)
MODEL = "gemini-3.5-flash-lite"
print("Gemini client initialized successfully.")


MAX_REACT_ITERATIONS = 3
MAX_IMPROVEMENT_ITERATIONS = 3

QUALITY_THRESHOLD = 8.0

print("Configuration loaded.")

def search_interview_concept(query: str) -> dict:
    """
    Searches Wikipedia for information related to an interview concept.
    Returns relevant titles and summaries.
    """

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 3
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")

            results.append({
                "title": title,
                "snippet": snippet
            })

        if not results:
            return {
                "success": False,
                "message": "No relevant results found."
            }

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Search failed: {str(e)}"
        }

search_tool_declaration = {
    "name": "search_interview_concept",
    "description": (
        "Searches an external knowledge source for information "
        "about machine learning, data science, statistics, SQL, "
        "Python, NLP, AI, and other technical interview concepts. "
        "Use this tool when external information would improve "
        "the accuracy or completeness of the answer."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The technical concept or question to search for."
                )
            }
        },
        "required": ["query"]
    }
}

tools = types.Tool(
    function_declarations=[search_tool_declaration]
)

tool_config = types.GenerateContentConfig(
    tools=[tools]
)

REACT_SYSTEM_PROMPT = """
You are an Interview Preparation Agent.

Your job is to answer technical interview questions accurately,
clearly, and in an interview-ready way.

You have access to a search_interview_concept tool.

Follow this workflow:

1. Understand the user's interview question.
2. Decide whether external retrieval would improve the answer.
3. If needed, call the search_interview_concept tool.
4. Observe the returned information.
5. Decide whether more information is needed.
6. If more information is needed, use the tool again.
7. If enough information is available, produce the final answer.

Important:
- Do not use the tool unnecessarily.
- Do not invent information from search results.
- Keep the final answer suitable for a technical interview.
- Include examples when they improve understanding.
- Do not reveal private chain-of-thought.
- You may briefly state the action taken, such as
  "I searched for additional information about X."
"""

def run_react_agent(question, max_iterations=3):

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=REACT_SYSTEM_PROMPT + "\n\nUser Question:\n" + question
                )
            ]
        )
    ]

    trace = []

    for iteration in range(1, max_iterations + 1):

        print(f"\n{'=' * 60}")
        print(f"REACT ITERATION {iteration}")
        print(f"{'=' * 60}")

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=tool_config
        )

        model_content = response.candidates[0].content

        function_calls = []

        for part in model_content.parts:
            if part.function_call:
                function_calls.append(part.function_call)

        # CASE 1: No tool call → final answer

        if not function_calls:

            final_text = response.text

            trace.append({
                "iteration": iteration,
                "action": "final_answer",
                "observation": "No further tool required."
            })

            print("\nAgent decided that no additional tool was required.")
            print("\nFINAL REACT ANSWER:\n")
            print(final_text)

            return {
                "answer": final_text,
                "trace": trace,
                "iterations": iteration,
                "max_iterations_reached": False
            }

        # CASE 2: Tool call requested

        contents.append(model_content)

        for function_call in function_calls:

            tool_name = function_call.name
            tool_args = function_call.args

            print(f"\nACTION: {tool_name}")
            print(f"ARGUMENTS: {tool_args}")

            if tool_name == "search_interview_concept":

                query = tool_args.get("query", "")

                result = search_interview_concept(query)

                print("\nOBSERVATION:")
                print(json.dumps(result, indent=2))

                trace.append({
                    "iteration": iteration,
                    "action": tool_name,
                    "arguments": dict(tool_args),
                    "observation": result
                })

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": result}
                )

                contents.append(
                    types.Content(
                        role="user",
                        parts=[function_response_part]
                    )
                )

            else:

                result = {
                    "success": False,
                    "message": f"Unknown tool: {tool_name}"
                }

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"result": result}
                            )
                        ]
                    )
                )

    # Maximum iteration reached

    print("\nMaximum ReAct iterations reached.")

    return {
        "answer": response.text,
        "trace": trace,
        "iterations": max_iterations,
        "max_iterations_reached": True
    }


def evaluate_answer(question, answer):

    prompt = f"""
{EVALUATION_PROMPT}

INTERVIEW QUESTION:
{question}

ANSWER TO EVALUATE:
{answer}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    evaluation_text = response.text.strip()

    # Remove Markdown JSON code fences if Gemini adds them
    if evaluation_text.startswith("```json"):
        evaluation_text = evaluation_text[7:]

    elif evaluation_text.startswith("```"):
        evaluation_text = evaluation_text[3:]

    if evaluation_text.endswith("```"):
        evaluation_text = evaluation_text[:-3]

    evaluation_text = evaluation_text.strip()

    try:
        evaluation = json.loads(evaluation_text)

    except json.JSONDecodeError:

        print("Evaluator did not return valid JSON.")
        print("\nRaw evaluator response:")
        print(response.text)

        return {
            "accuracy": 0,
            "relevance": 0,
            "completeness": 0,
            "clarity": 0,
            "hallucination_free": 0,
            "overall_score": 0,
            "strengths": [],
            "weaknesses": ["Evaluator returned invalid JSON."],
            "improvements": []
        }

    return evaluation

EVALUATION_PROMPT = """
You are an expert technical interview evaluator.

Evaluate the given interview answer using these five criteria:

1. Accuracy
   - Are the technical statements correct?

2. Relevance
   - Does the answer directly address the interview question?

3. Completeness
   - Does it cover the important points needed for a good interview answer?

4. Clarity
   - Is the explanation easy to understand and well structured?

5. Hallucination-free
   - Does the answer avoid unsupported or invented claims?

Give each criterion a score from 1 to 10.

Then calculate the overall score as the average of the five scores.

Also provide:
- strengths
- weaknesses
- specific improvement suggestions

Return ONLY valid JSON in this structure:

{
    "accuracy": 0,
    "relevance": 0,
    "completeness": 0,
    "clarity": 0,
    "hallucination_free": 0,
    "overall_score": 0,
    "strengths": [],
    "weaknesses": [],
    "improvements": []
}
"""

def generate_critique(question, answer, evaluation):

    prompt = f"""
You are a strict technical interview answer critic.

Review the interview answer using the evaluation below.

INTERVIEW QUESTION:
{question}

CURRENT ANSWER:
{answer}

EVALUATION:
{json.dumps(evaluation, indent=2)}

Your task is to identify the most important weaknesses
that should be fixed before the answer is considered
interview-ready.

Focus on:
- Technical mistakes
- Missing important concepts
- Irrelevant information
- Unclear explanations
- Unsupported claims
- Poor interview structure

If there are no meaningful weaknesses, say that the answer
does not require improvement.

Return a concise critique with specific improvement instructions.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text

def improve_answer(question, answer, critique):

    prompt = f"""
You are an expert technical interview answer improver.

Improve the answer based on the critique provided below.

INTERVIEW QUESTION:
{question}

CURRENT ANSWER:
{answer}

CRITIQUE:
{critique}

Instructions:
- Fix all important technical errors.
- Add missing important information.
- Remove irrelevant information.
- Improve clarity and structure.
- Keep the answer suitable for a technical interview.
- Do not introduce unsupported or invented information.
- Preserve correct information from the original answer.
- Make the answer concise but sufficiently detailed.

Return ONLY the improved interview answer.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


def run_improvement_loop(question, initial_answer, max_iterations=3):

    current_answer = initial_answer
    improvement_trace = []

    for iteration in range(1, max_iterations + 1):

        print(f"\n{'=' * 60}")
        print(f"IMPROVEMENT ITERATION {iteration}")
        print(f"{'=' * 60}")

        # -----------------------------------------------
        # STEP 1: Evaluate current answer
        # -----------------------------------------------

        evaluation = evaluate_answer(
            question,
            current_answer
        )

        print("\nEVALUATION:")
        print(json.dumps(evaluation, indent=2))

        score = evaluation.get("overall_score", 0)

        # -----------------------------------------------
        # STEP 2: Check quality threshold
        # -----------------------------------------------
        weaknesses = evaluation.get("weaknesses", [])

        if score >= QUALITY_THRESHOLD and not weaknesses:

            print(
                f"\n✅ Quality threshold reached: "
                f"{score} >= {QUALITY_THRESHOLD}"
            )

            improvement_trace.append({
                "iteration": iteration,
                "score": score,
                "action": "stop",
                "reason": "Quality threshold reached"
            })

            return {
                "final_answer": current_answer,
                "final_score": score,
                "evaluation": evaluation,
                "trace": improvement_trace,
                "iterations": iteration,
                "max_iterations_reached": False
            }

        # -----------------------------------------------
        # STEP 3: Generate critique
        # -----------------------------------------------

        critique = generate_critique(
            question,
            current_answer,
            evaluation
        )

        print("\nCRITIQUE:")
        print(critique)

        # -----------------------------------------------
        # STEP 4: Improve the answer
        # -----------------------------------------------

        improved_answer = improve_answer(
            question,
            current_answer,
            critique
        )

        print("\nIMPROVED ANSWER:")
        print(improved_answer)

        # -----------------------------------------------
        # STEP 5: Save this iteration
        # -----------------------------------------------

        improvement_trace.append({
            "iteration": iteration,
            "score": score,
            "evaluation": evaluation,
            "critique": critique,
            "answer_before": current_answer,
            "answer_after": improved_answer,
            "action": "improve"
        })

        # -----------------------------------------------
        # STEP 6: Replace old answer with new answer
        # -----------------------------------------------

        current_answer = improved_answer

    # ---------------------------------------------------
    # Maximum iterations reached
    # ---------------------------------------------------

    print("\n⚠️ Maximum improvement iterations reached.")

    final_evaluation = evaluate_answer(
        question,
        current_answer
    )

    final_score = final_evaluation.get(
        "overall_score",
        0
    )

    return {
        "final_answer": current_answer,
        "final_score": final_score,
        "evaluation": final_evaluation,
        "trace": improvement_trace,
        "iterations": max_iterations,
        "max_iterations_reached": True
    }


def run_complete_agent(question):

    print("\n" + "=" * 60)
    print("🚀 STARTING COMPLETE INTERVIEW AGENT")
    print("=" * 60)

    # -----------------------------------------------
    # PART 1: ReAct Agent
    # -----------------------------------------------

    print("\n🧠 PART 1 — ReAct Agent")

    react_result = run_react_agent(
        question,
        max_iterations=MAX_REACT_ITERATIONS
    )

    initial_answer = react_result["answer"]

    print("\nInitial ReAct Answer:")
    print(initial_answer)

    # -----------------------------------------------
    # PART 2: Improvement Loop
    # -----------------------------------------------

    print("\n" + "=" * 60)
    print("🔄 PART 2 — IMPROVEMENT LOOP")
    print("=" * 60)

    improvement_result = run_improvement_loop(
        question,
        initial_answer,
        max_iterations=MAX_IMPROVEMENT_ITERATIONS
    )

    # -----------------------------------------------
    # Final Result
    # -----------------------------------------------

    print("\n" + "=" * 60)
    print("🎯 FINAL INTERVIEW ANSWER")
    print("=" * 60)

    print(improvement_result["final_answer"])

    return {
        "question": question,
        "initial_answer": initial_answer,
        "react_trace": react_result["trace"],
        "improvement_trace": improvement_result["trace"],
        "final_answer": improvement_result["final_answer"],
        "final_score": improvement_result["final_score"],
        "iterations": improvement_result["iterations"],
        "max_iterations_reached": improvement_result[
            "max_iterations_reached"
        ]
    }
if __name__ == "__main__":
    question = input("Enter your interview question: ")

    result = run_complete_agent(question)

    print("\nFinal Answer:")
    print(result["final_answer"])



