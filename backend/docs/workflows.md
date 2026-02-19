# Workflow Documentation

## Overview

The Podd Health Assistant uses LangGraph for managing complex healthcare workflows. Workflows define the sequence of operations for various tasks like daily summaries, health monitoring, and AI agent coordination.

**Dual-Database Architecture**:
- **SQLite**: Stores ONLY authentication data (Users, RefreshTokens)
- **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, Schedules, Activities, Reminders, Chat)

## Workflow Architecture

### LangGraph Integration

LangGraph is used to create stateful, multi-agent workflows with human-in-the-loop capabilities. It provides:
- **State Management**: Persistent state across workflow steps
- **Agent Coordination**: Multiple AI agents working together
- **Human-in-the-loop**: Integrate human decisions into automated processes
- **Memory & Checkpoints**: Save workflow state for recovery
- **Reusable Graphs**: Define and reuse workflow patterns

### LocusGraph as Primary Data Store

All health-related data is stored in LocusGraph SDK with specific event schemas:
- **Vitals Events**: `context_id: vitals:<id>` with blood_pressure_systolic, heart_rate, etc.
- **FoodLog Events**: `context_id: food:<id>` with description, calories, meal_type
- **Medication Events**: `context_id: medication:<id>` with name, dosage, frequency
- **SleepLog Events**: `context_id: sleep:<id>` with sleep_start, sleep_end, quality
- **ExerciseLog Events**: `context_id: exercise:<id>` with exercise_type, duration_minutes
- **MoodLog Events**: `context_id: mood:<id>` with mood, energy_level, notes
- **WaterLog Events**: `context_id: water:<id>` with amount_ml

**Key Integration Points**:
- `store_event()`: Store health data in LocusGraph
- `retrieve_context()`: Retrieve health data by type and user_id
- `generate_insights()`: Generate health insights from LocusGraph events
- `update_event()`: Update existing health events
- `delete_event()`: Delete health events

## Workflow Types

### 1. Daily Summary Workflow

**Purpose**: Generate comprehensive daily health summaries

**Flow**:
```
1. Collect Daily Data
   - Health vitals from LocusGraph
   - Medication logs from LocusGraph
   - Activity logs (food, exercise) from LocusGraph
   - Mood and sleep logs from LocusGraph

2. Analyze Data
   - Calculate health metrics
   - Identify trends
   - Check medication compliance

3. Generate Insights
   - Generate health score
   - Identify anomalies
   - Create recommendations

4. Create Summary
   - Format summary report
   - Include key insights
   - Suggest next steps
```

**State Schema**:
```python
class DailySummaryState(TypedDict):
    user_id: str
    date: date
    collected_data: Dict[str, Any]
    analyzed_data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    health_score: float
    summary_text: str
    completed: bool = False
```

**Workflow Steps**:
```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

class DailySummaryState(TypedDict):
    user_id: str
    date: date
    collected_data: Dict[str, Any]
    analyzed_data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    health_score: float
    summary_text: str
    completed: bool

def collect_data(state: DailySummaryState) -> DailySummaryState:
    """Collect all daily data from LocusGraph"""
    # Fetch health vitals from LocusGraph
    vitals = await locusgraph_service.retrieve_context(
        context_type="vitals",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    # Fetch medication logs from LocusGraph
    medication_logs = await locusgraph_service.retrieve_context(
        context_type="medication",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    # Fetch activity logs from LocusGraph
    food_logs = await locusgraph_service.retrieve_context(
        context_type="food",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    exercise_logs = await locusgraph_service.retrieve_context(
        context_type="exercise",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    sleep_logs = await locusgraph_service.retrieve_context(
        context_type="sleep",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    mood_logs = await locusgraph_service.retrieve_context(
        context_type="mood",
        user_id=state["user_id"],
        filters={"min_date": state["date"], "max_date": state["date"]}
    )

    # Store in state
    state["collected_data"] = {
        "vitals": vitals,
        "medication": medication_logs,
        "food": food_logs,
        "exercise": exercise_logs,
        "sleep": sleep_logs,
        "mood": mood_logs
    }
    return state

def analyze_data(state: DailySummaryState) -> DailySummaryState:
    """Analyze collected data"""
    # Calculate average heart rate
    avg_heart_rate = calculate_average_heart_rate(state["collected_data"]["vitals"])

    # Check medication compliance
    compliance_rate = calculate_medication_compliance(
        state["collected_data"]["medication"]
    )

    # Analyze activity patterns
    total_calories = sum([food["calories"] for food in state["collected_data"]["food"]])
    total_steps = sum([exercise["duration_minutes"] * 100 for exercise in state["collected_data"]["exercise"]])

    # Identify health trends
    health_trends = identify_health_trends(state["collected_data"])

    state["analyzed_data"] = {
        "avg_heart_rate": avg_heart_rate,
        "medication_compliance": compliance_rate,
        "total_calories": total_calories,
        "total_steps": total_steps,
        "health_trends": health_trends
    }
    return state

def generate_insights(state: DailySummaryState) -> DailySummaryState:
    """Generate health insights using LocusGraph"""
    # Use LocusGraph to get historical context
    historical_context = await locusgraph_service.generate_insights(
        user_id=state["user_id"],
        query={"days": 30}
    )

    # Generate insights based on AI analysis
    health_score = calculate_health_score(state["analyzed_data"], historical_context)

    insights = generate_health_insights(
        state["analyzed_data"],
        historical_context
    )

    state["health_score"] = health_score
    state["insights"] = insights
    return state

def create_recommendations(state: DailySummaryState) -> DailySummaryState:
    """Create personalized recommendations"""
    recommendations = generate_personalized_recommendations(
        state["analyzed_data"],
        state["insights"]
    )

    state["recommendations"] = recommendations
    return state

def generate_summary_text(state: DailySummaryState) -> DailySummaryState:
    """Generate formatted summary text"""
    summary = format_daily_summary(
        state["date"],
        state["health_score"],
        state["insights"],
        state["recommendations"]
    )

    state["summary_text"] = summary
    return state

def complete_workflow(state: DailySummaryState) -> DailySummaryState:
    """Mark workflow as completed"""
    state['completed'] = True
    return state

# Build workflow graph
workflow = StateGraph(DailySummaryState)

# Add nodes
workflow.add_node("collect_data", collect_data)
workflow.add_node("analyze_data", analyze_data)
workflow.add_node("generate_insights", generate_insights)
workflow.add_node("create_recommendations", create_recommendations)
workflow.add_node("generate_summary_text", generate_summary_text)
workflow.add_node("complete_workflow", complete_workflow)

# Add edges
workflow.set_entry_point("collect_data")
workflow.add_edge("collect_data", "analyze_data")
workflow.add_edge("analyze_data", "generate_insights")
workflow.add_edge("generate_insights", "create_recommendations")
workflow.add_edge("create_recommendations", "generate_summary_text")
workflow.add_edge("generate_summary_text", "complete_workflow")
workflow.add_edge("complete_workflow", END)

# Compile workflow
app = workflow.compile()
```

**Usage**:
```python
from datetime import date

# Initialize state
initial_state = {
    "user_id": "user-123",
    "date": date.today(),
    "collected_data": {},
    "analyzed_data": {},
    "insights": [],
    "recommendations": [],
    "health_score": 0.0,
    "summary_text": "",
    "completed": False
}

# Execute workflow
result = app.invoke(initial_state)

# Access results
print(result["summary_text"])
print(result["health_score"])
print(result["insights"])
```

---

### 2. Health Monitoring Workflow

**Purpose**: Monitor health vitals and trigger alerts

**Flow**:
```
1. Receive Vitals Input
   - New health data received
   - Validate input

2. Compare with Thresholds
   - Compare heart rate
   - Check blood pressure
   - Monitor temperature
   - Verify oxygen levels

3. Detect Anomalies
   - Identify abnormal readings
   - Compare with historical data
   - Check for trends

4. Trigger Alerts (if needed)
   - Send notifications
   - Alert emergency contacts
   - Create health log entry in LocusGraph

5. Generate Recommendations
   - Suggest actions
   - Provide health tips
```

**State Schema**:
```python
class HealthMonitoringState(TypedDict):
    user_id: str
    vitals_data: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    thresholds: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    alerts_triggered: List[str]
    recommendations: List[str]
    completed: bool = False
```

**Workflow Steps**:
```python
def validate_input(state: HealthMonitoringState) -> HealthMonitoringState:
    """Validate vitals data"""
    # Check required fields
    required_fields = ["heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic"]
    for field in required_fields:
        if field not in state["vitals_data"]:
            raise ValueError(f"Missing required field: {field}")

    # Validate ranges
    validate_heart_rate(state["vitals_data"]["heart_rate"])
    validate_blood_pressure(state["vitals_data"]["blood_pressure_systolic"], state["vitals_data"]["blood_pressure_diastolic"])
    validate_temperature(state["vitals_data"]["temperature"])
    validate_oxygen_level(state["vitals_data"]["oxygen_level"])

    return state

def compare_with_thresholds(state: HealthMonitoringState) -> HealthMonitoringState:
    """Compare vitals with thresholds"""
    # Heart rate > 120 or < 60
    heart_rate = state["vitals_data"]["heart_rate"]
    if heart_rate > 120 or heart_rate < 60:
        state["anomalies"].append({
            "field": "heart_rate",
            "value": heart_rate,
            "threshold": "60-120",
            "severity": "warning"
        })

    # Blood pressure > 140/90
    systolic = state["vitals_data"]["blood_pressure_systolic"]
    diastolic = state["vitals_data"]["blood_pressure_diastolic"]
    if systolic > 140 or diastolic > 90:
        state["anomalies"].append({
            "field": "blood_pressure",
            "value": f"{systolic}/{diastolic}",
            "threshold": "<140/90",
            "severity": "warning"
        })

    # Temperature > 38°C
    if state["vitals_data"]["temperature"] > 38.0:
        state["anomalies"].append({
            "field": "temperature",
            "value": state["vitals_data"]["temperature"],
            "threshold": "<38°C",
            "severity": "moderate"
        })

    # Oxygen < 95%
    if state["vitals_data"]["oxygen_level"] < 95:
        state["anomalies"].append({
            "field": "oxygen_level",
            "value": state["vitals_data"]["oxygen_level"],
            "threshold": ">95%",
            "severity": "high"
        })

    return state

def check_historical_trends(state: HealthMonitoringState) -> HealthMonitoringState:
    """Check for trends in historical data from LocusGraph"""
    # Get historical vitals from LocusGraph
    historical_data = await locusgraph_service.retrieve_context(
        context_type="vitals",
        user_id=state["user_id"],
        filters={"min_date": "2026-02-01"}  # Last 30 days
    )

    state["historical_data"] = historical_data

    # Identify gradual increases/decreases
    heart_rate_trend = analyze_trend([v["heart_rate"] for v in historical_data])

    # Check for patterns
    patterns = identify_patterns(historical_data)

    if heart_rate_trend == "increasing":
        state["anomalies"].append({
            "field": "heart_rate_trend",
            "value": "increasing",
            "threshold": "stable",
            "severity": "moderate"
        })

    return state

def detect_anomalies(state: HealthMonitoringState) -> HealthMonitoringState:
    """Detect health anomalies"""
    # Compare with historical average
    avg_heart_rate = calculate_average_heart_rate([v["heart_rate"] for v in state["historical_data"]])
    current_heart_rate = state["vitals_data"]["heart_rate"]

    if abs(current_heart_rate - avg_heart_rate) > 20:
        state["anomalies"].append({
            "field": "heart_rate",
            "value": current_heart_rate,
            "average": avg_heart_rate,
            "severity": "warning"
        })

    # Identify outliers
    outliers = identify_outliers([v["heart_rate"] for v in state["historical_data"]], current_heart_rate)

    if outliers:
        for outlier in outliers:
            state["anomalies"].append({
                "field": "heart_rate",
                "value": current_heart_rate,
                "reason": outlier,
                "severity": "moderate"
            })

    return state

def trigger_alerts(state: HealthMonitoringState) -> HealthMonitoringState:
    """Trigger alerts for anomalies"""
    if state["anomalies"]:
        for anomaly in state["anomalies"]:
            if anomaly["severity"] in ["high", "moderate"]:
                # Store alert in LocusGraph
                await locusgraph_service.store_event(
                    event_kind="fact",
                    context_id=f"alert:{uuid.uuid4()}",
                    payload={
                        "type": anomaly["field"],
                        "severity": anomaly["severity"],
                        "value": anomaly["value"],
                        "message": generate_alert_message(anomaly),
                        "logged_at": datetime.utcnow().isoformat()
                    }
                )

                # Send notification
                await notification_service.send_alert(
                    user_id=state["user_id"],
                    alert=anomaly
                )

                state["alerts_triggered"].append(anomaly["field"])

    return state

def generate_recommendations(state: HealthMonitoringState) -> HealthMonitoringState:
    """Generate health recommendations"""
    recommendations = []

    if "heart_rate" in [a["field"] for a in state["anomalies"]]:
        recommendations.append("Your heart rate is outside normal range. Consider resting and monitoring.")

    if "blood_pressure" in [a["field"] for a in state["anomalies"]]:
        recommendations.append("Monitor your blood pressure. Avoid stress and excessive salt intake.")

    if "oxygen_level" in [a["field"] for a in state["anomalies"]]:
        recommendations.append("Your oxygen level is low. Seek medical attention if it doesn't improve.")

    state["recommendations"] = recommendations
    return state
```

---

### 3. Medication Management Workflow

**Purpose**: Manage medication schedules and track adherence

**Flow**:
```
1. Schedule Medication
   - Create medication schedule in LocusGraph
   - Set reminder times
   - Configure recurrence

2. Track Intake
   - Log medication taken via LocusGraph
   - Verify against schedule
   - Record dosage

3. Monitor Adherence
   - Calculate compliance rate
   - Identify missed doses
   - Flag potential issues

4. Send Reminders
   - Send notifications
   - Alert for missed doses
   - Refill reminders

5. Refill Management
   - Track quantity remaining
   - Send refill alerts
   - Record prescription details
```

**State Schema**:
```python
class MedicationWorkflowState(TypedDict):
    user_id: str
    medication_schedule: Dict[str, Any]
    intake_logs: List[Dict[str, Any]]
    adherence_score: float
    missed_doses: List[Dict[str, Any]]
    refill_alerts: List[Dict[str, Any]]
    notifications_sent: List[str]
    completed: bool = False
```

**Workflow Steps**:
```python
def create_schedule(state: MedicationWorkflowState) -> MedicationWorkflowState:
    """Create medication schedule in LocusGraph"""
    # Validate medication data
    validate_medication_data(state["medication_schedule"])

    # Store medication in LocusGraph
    schedule_id = str(uuid.uuid4())
    await locusgraph_service.store_event(
        event_kind="fact",
        context_id=f"med_schedule:{schedule_id}",
        payload={
            "medication_id": state["medication_schedule"]["name"],
            "dosage": state["medication_schedule"]["dosage"],
            "frequency": state["medication_schedule"]["frequency"],
            "times": state["medication_schedule"]["times"],
            "days": state["medication_schedule"]["days"],
            "quantity": state["medication_schedule"]["quantity"],
            "created_at": datetime.utcnow().isoformat()
        }
    )

    state["medication_schedule"]["id"] = schedule_id
    return state

def log_intake(state: MedicationWorkflowState) -> MedicationWorkflowState:
    """Log medication intake in LocusGraph"""
    intake_log_id = str(uuid.uuid4())

    # Store intake log in LocusGraph
    await locusgraph_service.store_event(
        event_kind="fact",
        context_id=f"medication:{intake_log_id}",
        payload={
            "schedule_id": state["medication_schedule"]["id"],
            "dosage": state["medication_schedule"]["dosage"],
            "taken_at": datetime.utcnow().isoformat(),
            "notes": state["medication_schedule"].get("notes", ""),
            "logged_at": datetime.utcnow().isoformat()
        },
        related_to=[f"med_schedule:{state['medication_schedule']['id']}"]
    )

    state["intake_logs"].append({
        "id": intake_log_id,
        "taken_at": datetime.utcnow(),
        "dosage": state["medication_schedule"]["dosage"]
    })

    return state

def calculate_adherence(state: MedicationWorkflowState) -> MedicationWorkflowState:
    """Calculate medication adherence from LocusGraph data"""
    # Retrieve all intake logs for the schedule
    intake_logs = await locusgraph_service.retrieve_context(
        context_type="medication",
        user_id=state["user_id"],
        filters={"schedule_id": state["medication_schedule"]["id"]}
    )

    state["intake_logs"] = intake_logs

    # Calculate compliance rate
    scheduled_doses = len(state["medication_schedule"]["times"]) * 7  # Daily for a week
    actual_doses = len(intake_logs)

    if scheduled_doses > 0:
        state["adherence_score"] = (actual_doses / scheduled_doses) * 100
    else:
        state["adherence_score"] = 100

    # Identify missed doses
    missed_doses = []
    for scheduled_time in state["medication_schedule"]["times"]:
        if not any(log["taken_at"] and is_after_todays_time(log["taken_at"], scheduled_time) for log in intake_logs):
            missed_doses.append({
                "time": scheduled_time,
                "day": datetime.now().strftime("%A")
            })

    state["missed_doses"] = missed_doses
    return state

def send_reminders(state: MedicationWorkflowState) -> MedicationWorkflowState:
    """Send medication reminders"""
    current_time = datetime.now().time()

    for scheduled_time in state["medication_schedule"]["times"]:
        time_obj = parse_time(scheduled_time)

        # Check if it's time to take medication
        if current_time >= time_obj and current_time < add_minutes(time_obj, 15):
            # Send reminder notification
            message = generate_medication_reminder(
                state["medication_schedule"]["name"],
                scheduled_time
            )

            await notification_service.send(
                user_id=state["user_id"],
                title="Medication Reminder",
                message=message
            )

            state["notifications_sent"].append(f"Reminded at {scheduled_time}")

    return state

def manage_refills(state: MedicationWorkflowState) -> MedicationWorkflowState:
    """Manage medication refills"""
    # Check quantity remaining
    quantity_remaining = state["medication_schedule"]["quantity"]

    if quantity_remaining <= 10:
        # Send refill alert
        refill_alert = {
            "medication": state["medication_schedule"]["name"],
            "dosage": state["medication_schedule"]["dosage"],
            "quantity_remaining": quantity_remaining,
            "timestamp": datetime.utcnow().isoformat()
        }

        state["refill_alerts"].append(refill_alert)

        # Send notification
        await notification_service.send_alert(
            user_id=state["user_id"],
            alert=refill_alert
        )

    return state
```

---

### 4. AI Chat Agent Workflow

**Purpose**: Handle AI-powered chat interactions

**Flow**:
```
1. Receive User Message
   - Parse user input
   - Extract context

2. Retrieve Context from LocusGraph
   - Get user profile
   - Check health history
   - Review recent logs

3. Generate Response
   - Use AI model to generate response
   - Consider user context
   - Provide helpful information

4. Update Memory in LocusGraph
   - Store conversation
   - Update user preferences
   - Remember important information

5. Return Response
   - Send to user
   - Log interaction
```

**State Schema**:
```python
class ChatState(TypedDict):
    user_id: str
    message: str
    context: Dict[str, Any]
    response: str
    memory_updates: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    completed: bool = False
```

**Workflow Steps**:
```python
def retrieve_context(state: ChatState) -> ChatState:
    """Retrieve relevant context from LocusGraph"""
    # Get user profile
    profile = await locusgraph_service.retrieve_context(
        context_type="profile",
        user_id=state["user_id"]
    )

    # Get recent health data
    recent_vitals = await locusgraph_service.retrieve_context(
        context_type="vitals",
        user_id=state["user_id"],
        filters={"min_date": "2026-02-11"}  # Last 7 days
    )

    recent_health_data = await locusgraph_service.generate_insights(
        user_id=state["user_id"],
        query={"days": 7}
    )

    # Retrieve previous conversations
    conversation_history = await locusgraph_service.retrieve_context(
        context_type="chat",
        user_id=state["user_id"],
        filters={"limit": 50}
    )

    state["context"] = {
        "profile": profile,
        "recent_vitals": recent_vitals,
        "recent_health_data": recent_health_data,
        "conversation_history": conversation_history
    }

    return state

def process_message(state: ChatState) -> ChatState:
    """Process user message with AI"""
    # Generate prompt with context
    prompt = generate_chat_prompt(
        state["message"],
        state["context"]
    )

    # Call AI model
    response = await ai_service.generate_response(prompt)

    state["response"] = response
    return state

def generate_response(state: ChatState) -> ChatState:
    """Generate formatted response"""
    # Add context to response
    response = add_context_to_response(
        state["response"],
        state["context"]
    )

    # Check for escalation
    if is_escalation_needed(state["response"]):
        # Send to human agent
        await notification_service.send_alert(
            user_id=state["user_id"],
            alert={"type": "chat_escalation", "message": state["response"]}
        )

    state["response"] = response
    return state

def update_memory(state: ChatState) -> ChatState:
    """Update conversation memory in LocusGraph"""
    # Store current message
    message_id = str(uuid.uuid4())
    await locusgraph_service.store_event(
        event_kind="action",
        context_id=f"chat:{message_id}",
        payload={
            "user_message": state["message"],
            "timestamp": datetime.utcnow().isoformat()
        },
        related_to=[f"chat:{state['conversation_history'][-1]['id']}" if state["conversation_history"] else None]
    )

    # Update user preferences if mentioned
    if "preference" in state["message"].lower():
        await locusgraph_service.store_event(
            event_kind="fact",
            context_id=f"pref:{str(uuid.uuid4())}",
            payload={
                "topic": "preference",
                "value": state["message"]
            }
        )

    # Update conversation history
    state["conversation_history"].append({
        "id": message_id,
        "message": state["message"],
        "timestamp": datetime.utcnow().isoformat()
    })

    return state

def return_response(state: ChatState) -> ChatState:
    """Return response to user"""
    state['completed'] = True
    return state
```

---

## AI Agent Framework

### Agent Types

The system includes specialized AI agents for different domains:

#### 1. Health Query Agent
```python
class HealthQueryAgent(BaseModel):
    name: str = "Health Query Agent"
    role: str = "Provide health information and answer health-related questions"

    def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process health-related queries"""
        # Retrieve context from LocusGraph
        health_data = locusgraph_service.retrieve_context(
            context_type="vitals",
            user_id=context["user_id"]
        )

        # Generate response with context
        response = self.ai_model.generate(
            prompt=f"Answer this health question: {query}\n\nContext: {health_data}",
            temperature=0.7
        )

        return response
```

#### 2. Medication Agent
```python
class MedicationAgent(BaseModel):
    name: str = "Medication Agent"
    role: str = "Provide medication information and adherence support"

    def process_medication(self, medication_name: str, action: str) -> str:
        """Process medication-related requests"""
        # Retrieve medication schedule from LocusGraph
        medication_schedules = locusgraph_service.retrieve_context(
            context_type="med_schedule",
            filters={"medication_id": medication_name}
        )

        # Provide medication information with adherence data
        response = self.ai_model.generate(
            prompt=f"Help with {action} for {medication_name}\n\nSchedule: {medication_schedules}",
            temperature=0.7
        )

        return response
```

#### 3. Recommendation Agent
```python
class RecommendationAgent(BaseModel):
    name: str = "Recommendation Agent"
    role: str = "Provide personalized health recommendations"

    def generate_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate health recommendations from LocusGraph data"""
        # Get health insights from LocusGraph
        insights = locusgraph_service.generate_insights(
            user_id=user_data["user_id"],
            query={"topic": "health_recommendations"}
        )

        # Generate personalized recommendations
        recommendations = self.ai_model.generate(
            prompt=f"Generate health recommendations based on this data:\n{insights}",
            temperature=0.8
        )

        return recommendations
```

#### 4. General Chat Agent
```python
class GeneralChatAgent(BaseModel):
    name: str = "General Chat Agent"
    role: str = "Handle general conversations and provide support"

    def process_chat(self, message: str, context: Dict[str, Any]) -> str:
        """Process general chat messages"""
        # Retrieve conversation history from LocusGraph
        conversation = locusgraph_service.retrieve_context(
            context_type="chat",
            user_id=context["user_id"],
            filters={"limit": 20}
        )

        # Generate response with context
        response = self.ai_model.generate(
            prompt=f"Chat with user. Context: {conversation}. User says: {message}",
            temperature=0.7
        )

        return response
```

### Agent Orchestration

Agents work together in workflows:

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Initialize AI models
openai_model = ChatOpenAI(model="gpt-4", temperature=0.7)
anthropic_model = ChatAnthropic(model="claude-3-opus", temperature=0.7)

# Create agents
health_agent = HealthQueryAgent(model=openai_model)
medication_agent = MedicationAgent(model=anthropic_model)
recommendation_agent = RecommendationAgent(model=openai_model)
general_agent = GeneralChatAgent(model=anthropic_model)

# Create agent pool
agent_pool = {
    "health": health_agent,
    "medication": medication_agent,
    "recommendation": recommendation_agent,
    "general": general_agent
}
```

---

## LocusGraph Memory Integration

### Purpose

LocusGraph provides long-term memory and context for AI interactions with structured event schemas.

### Usage

```python
from locusgraph_client import LocusGraphClient

# Initialize client
client = LocusGraphClient(
    api_url=settings.LOCUSGRAPH_API_URL,
    api_key=settings.LOCUSGRAPH_API_KEY,
    graph_id=settings.LOCUSGRAPH_GRAPH_ID
)

# Store health event
client.store_event(
    event_kind="fact",
    context_id="vitals:12345",
    payload={
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "logged_at": "2026-02-18T08:00:00Z"
    }
)

# Retrieve health context
context = client.retrieve_context(
    context_type="vitals",
    user_id="user_123",
    filters={"min_date": "2026-02-11"}
)

# Generate insights
insights = client.generate_insights(
    user_id="user_123",
    query={"topic": "heart_health", "days": 30}
)

# Update event
client.update_event(
    context_id="vitals:12345",
    updates={"heart_rate": 75, "logged_at": "2026-02-18T09:00:00Z"}
)

# Delete event
client.delete_event("vitals:12345")
```

### Event Schema Types

1. **Profile Events**: `context_id: profile:<user_id>` with date_of_birth, gender, height_cm, weight_kg, etc.
2. **Vitals Events**: `context_id: vitals:<id>` with blood_pressure_systolic, heart_rate, temperature, etc.
3. **FoodLog Events**: `context_id: food:<id>` with description, calories, meal_type, etc.
4. **Medication Events**: `context_id: medication:<id>` with name, dosage, frequency, etc.
5. **SleepLog Events**: `context_id: sleep:<id>` with sleep_start, sleep_end, quality, etc.
6. **ExerciseLog Events**: `context_id: exercise:<id>` with exercise_type, duration_minutes, etc.
7. **MoodLog Events**: `context_id: mood:<id>` with mood, energy_level, notes, etc.
8. **WaterLog Events**: `context_id: water:<id>` with amount_ml, etc.
9. **Chat Messages**: `context_id: chat:<id>` with user_message, ai_response, etc.

### Memory Types

1. **User Preferences**: Language, tone, preferences stored as LocusGraph events
2. **Health History**: Past conditions, treatments, vitals stored as LocusGraph events
3. **Interaction History**: Past conversations stored as chat message events
4. **Medical Information**: Relevant health data stored as vitals, medication events

---

## Memory Management

### Memory Components

```python
class WorkflowMemory(BaseModel):
    # Short-term memory
    current_state: Dict[str, Any]

    # Long-term memory (application memory)
    user_profile: Dict[str, Any]
    health_history: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]

    # External memory (LocusGraph)
    external_memory: Dict[str, Any]

    def store_in_short_term(self, key: str, value: Any) -> None:
        """Store value in short-term memory"""
        self.current_state[key] = value

    def retrieve_from_short_term(self, key: str) -> Any:
        """Retrieve value from short-term memory"""
        return self.current_state.get(key)

    def store_in_long_term(self, key: str, value: Any) -> None:
        """Store value in long-term memory"""
        self.user_profile[key] = value

    def retrieve_from_long_term(self, key: str) -> Any:
        """Retrieve value from long-term memory"""
        return self.user_profile.get(key)

    def save_to_external_memory(self, event: Dict[str, Any]) -> None:
        """Save to external memory (LocusGraph)"""
        # Store event in LocusGraph
        await locusgraph_service.store_event(
            event_kind=event.get("event_kind", "fact"),
            context_id=event.get("context_id", ""),
            payload=event.get("payload", {}),
            related_to=event.get("related_to", [])
        )

    def retrieve_from_external_memory(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve from external memory (LocusGraph)"""
        # Retrieve context from LocusGraph
        return await locusgraph_service.retrieve_context(
            context_type="all",
            user_id=self.current_state.get("user_id", ""),
            filters={}
        )
```

### Memory Pattern

```python
class MemoryPattern:
    def __init__(self):
        self.memory = WorkflowMemory()

    async def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with memory management"""

        # Load user context from long-term memory
        user_id = input_data.get("user_id")
        user_data = self.memory.retrieve_from_long_term(f"user:{user_id}")
        self.memory.external_memory = user_data

        # Process workflow
        result = await self.process(input_data)

        # Save results to long-term memory
        self.memory.store_in_long_term(f"user:{user_id}", user_data)

        # Save to external memory (LocusGraph)
        await self.memory.save_to_external_memory({
            "event_type": "workflow_completion",
            "user_id": user_id,
            "result": result
        })

        return result
```

---

## State Management

### State Definition

```python
from typing import TypedDict, Annotated, Sequence
from operator import add

class WorkflowState(TypedDict):
    user_id: str
    current_step: str
    data: Dict[str, Any]
    results: Annotated[Sequence[Dict[str, Any]], add]
    errors: List[str]
    completed: bool
    metadata: Dict[str, Any]
```

### State Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

# Create memory store
memory = MemorySaver()

# Bind memory to workflow
app = workflow.compile(checkpointer=memory)

# Thread configuration for persistent state
config = {
    "configurable": {
        "thread_id": "user-session-123"
    }
}

# Run workflow with state persistence
result = app.invoke(initial_state, config=config)

# Continue from previous state
result = app.invoke(
    {"user_id": "user-123"},
    config=config
)
```

---

## Workflow Orchestration

### Central Workflow Engine

```python
class WorkflowOrchestrator:
    def __init__(self):
        self.workflows = {
            "daily_summary": DailySummaryWorkflow(),
            "health_monitoring": HealthMonitoringWorkflow(),
            "medication_management": MedicationWorkflow(),
            "chat": ChatWorkflow()
        }

    async def execute_workflow(
        self,
        workflow_type: str,
        input_data: Dict[str, Any],
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow by type"""
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_type}")

        workflow = self.workflows[workflow_type]
        return await workflow.execute(input_data, config or {})

    def register_workflow(self, name: str, workflow: Any) -> None:
        """Register a new workflow"""
        self.workflows[name] = workflow
```

### Workflow Controller

```python
class WorkflowController:
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator

    async def trigger_daily_summary(self, user_id: str) -> Dict[str, Any]:
        """Trigger daily summary workflow"""
        return await self.orchestrator.execute_workflow(
            "daily_summary",
            {
                "user_id": user_id,
                "date": date.today()
            }
        )

    async def monitor_health(self, user_id: str, vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger health monitoring workflow"""
        return await self.orchestrator.execute_workflow(
            "health_monitoring",
            {
                "user_id": user_id,
                "vitals_data": vitals
            }
        )

    async def process_chat(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process chat message with AI"""
        return await self.orchestrator.execute_workflow(
            "chat",
            {
                "user_id": user_id,
                "message": message
            }
        )
```

---

## Workflow Execution Examples

### Example 1: Generate Daily Summary

```python
from datetime import date

# Initialize controller
controller = WorkflowController(WorkflowOrchestrator())

# Execute daily summary workflow
result = await controller.trigger_daily_summary("user-123")

print(f"Health Score: {result['health_score']}")
print(f"Summary: {result['summary_text']}")
print(f"Insights: {result['insights']}")
print(f"Recommendations: {result['recommendations']}")
```

### Example 2: Monitor Health Vitals

```python
# Monitor health with new vitals
result = await controller.monitor_health("user-123", {
    "heart_rate": 95,
    "blood_pressure": "130/85",
    "temperature": 37.5,
    "oxygen_level": 96
})

if result["anomalies"]:
    print("Anomalies detected:")
    for anomaly in result["anomalies"]:
        print(f"- {anomaly}")

print(f"Recommendations: {result['recommendations']}")
```

### Example 3: AI Chat Interaction

```python
# Process chat message
result = await controller.process_chat("user-123", "I'm feeling tired today")

print(f"Response: {result['response']}")
print(f"Conversation history: {len(result['conversation_history'])}")
```

---

## Workflow Testing

### Unit Testing Workflows

```python
import pytest
from datetime import date

@pytest.mark.asyncio
async def test_daily_summary_workflow():
    """Test daily summary workflow"""
    controller = WorkflowController(WorkflowOrchestrator())

    result = await controller.trigger_daily_summary("test-user")

    assert result["completed"] == True
    assert result["health_score"] >= 0
    assert result["health_score"] <= 100
    assert len(result["insights"]) > 0
    assert len(result["recommendations"]) > 0

@pytest.mark.asyncio
async def test_health_monitoring_anomalies():
    """Test health monitoring for anomalies"""
    controller = WorkflowController(WorkflowOrchestrator())

    result = await controller.monitor_health("test-user", {
        "heart_rate": 150,  # Abnormally high
        "blood_pressure": "160/100",  # Abnormally high
    })

    assert len(result["anomalies"]) > 0
    assert len(result["alerts_triggered"]) > 0
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_full_workflow_integration():
    """Test complete workflow integration"""
    # Setup
    controller = WorkflowController(WorkflowOrchestrator())

    # Execute workflow
    result = await controller.trigger_daily_summary("test-user")

    # Verify results
    assert result["completed"] == True

    # Verify memory updates
    # (add memory verification tests)
```

---

## Workflow Scheduling

### Scheduled Workflows

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time

class WorkflowScheduler:
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
        self.scheduler = AsyncIOScheduler()

    def schedule_daily_summary(self, user_id: str, time: time = time(8, 0)):
        """Schedule daily summary at specified time"""
        self.scheduler.add_job(
            self.execute_daily_summary,
            trigger='cron',
            hour=time.hour,
            minute=time.minute,
            args=[user_id]
        )

    async def execute_daily_summary(self, user_id: str):
        """Execute scheduled daily summary"""
        result = await self.orchestrator.execute_workflow(
            "daily_summary",
            {
                "user_id": user_id,
                "date": date.today()
            }
        )
        # Send summary to user
        # await notification_service.send(result["summary_text"])

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
```

---

## Best Practices

### Workflow Design

1. **Keep workflows focused**: Each workflow should have a single responsibility
2. **Use clear state management**: Define state schema explicitly
3. **Error handling**: Handle errors gracefully and log them
4. **Idempotency**: Make workflows idempotent for re-execution
5. **Performance**: Optimize for speed, especially for real-time workflows

### Agent Development

1. **Specialize agents**: Each agent should have a specific role
2. **Use appropriate models**: Choose models based on complexity
3. **Context awareness**: Agents should be aware of user context
4. **Safety checks**: Implement safety checks and validation
5. **Output validation**: Validate agent outputs

### Memory Management

1. **Separate concerns**: Keep short-term and long-term memory separate
2. **Memory updates**: Update memory consistently
3. **Memory retrieval**: Use appropriate memory retrieval strategies
4. **External memory**: Leverage LocusGraph for persistent memory
5. **Memory hygiene**: Clean up old memories periodically

### LocusGraph Integration

1. **Use appropriate event types**: Match event kind (fact, action, decision) to event type
2. **Use context_id prefixes**: Filter by context_id prefix (e.g., "vitals:", "food:") for efficient retrieval
3. **Use related_to links**: Link related events for efficient retrieval
4. **Include timestamps**: Use logged_at timestamps for date range queries
5. **Batch operations**: Use batch store_event() calls for performance

---

## Future Enhancements

### Planned Workflow Features

1. **Advanced Analytics Workflows**
   - Trend analysis
   - Predictive health scoring
   - Pattern recognition

2. **Care Coordination Workflows**
   - Care team notifications
   - Care plan generation
   - Care gap identification

3. **Medication Management Workflows**
   - Pill counting
   - Dispensing reminders
   - Side effect monitoring

4. **Wellness Workflows**
   - Goal tracking
   - Progress visualization
   - Motivation support

5. **Emergency Response Workflows**
   - SOS handling
   - Emergency notification chains
   - First responder coordination
