import gradio as gr
import json
from datetime import datetime
from typing import List, Dict, Tuple

class TodoApp:
    def __init__(self):
        self.todos = []
        self.next_id = 1
        
    def add_todo(self, text: str) -> Tuple[str, str]:
        """Add a new todo item"""
        if not text or text.strip() == "":
            return self.get_todos_display(), "Please enter a todo item"
        
        todo = {
            "id": self.next_id,
            "text": text.strip(),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.next_id += 1
        return self.get_todos_display(), ""
    
    def toggle_todo(self, todo_id: int) -> str:
        """Toggle completion status of a todo"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                break
        return self.get_todos_display()
    
    def delete_todo(self, todo_id: int) -> str:
        """Delete a todo item"""
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        return self.get_todos_display()
    
    def edit_todo(self, todo_id: int, new_text: str) -> str:
        """Edit a todo item"""
        if not new_text or new_text.strip() == "":
            return self.get_todos_display()
        
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["text"] = new_text.strip()
                break
        return self.get_todos_display()
    
    def clear_completed(self) -> str:
        """Remove all completed todos"""
        self.todos = [todo for todo in self.todos if not todo["completed"]]
        return self.get_todos_display()
    
    def get_todos_display(self) -> str:
        """Generate HTML display of todos"""
        if not self.todos:
            return """
            <div style="text-align: center; padding: 40px; color: #666;">
                <h3>No todos yet!</h3>
                <p>Add your first todo above to get started.</p>
            </div>
            """
        
        html = """
        <div style="max-width: 600px; margin: 0 auto;">
            <style>
                .todo-item {
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    margin: 8px 0;
                    background: white;
                    border: 1px solid #e1e5e9;
                    border-radius: 6px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .todo-completed {
                    background: #f8f9fa;
                    opacity: 0.7;
                }
                .todo-text {
                    flex: 1;
                    margin: 0 12px;
                    font-size: 16px;
                }
                .todo-completed .todo-text {
                    text-decoration: line-through;
                    color: #6c757d;
                }
                .todo-actions {
                    display: flex;
                    gap: 8px;
                }
                .btn-small {
                    padding: 4px 8px;
                    font-size: 12px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .btn-toggle {
                    background: #28a745;
                    color: white;
                }
                .btn-toggle.completed {
                    background: #6c757d;
                }
                .btn-delete {
                    background: #dc3545;
                    color: white;
                }
                .stats {
                    text-align: center;
                    margin: 20px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
            </style>
        """
        
        # Add stats
        total = len(self.todos)
        completed = sum(1 for todo in self.todos if todo["completed"])
        pending = total - completed
        
        html += f"""
            <div class="stats">
                <strong>Total: {total}</strong> | 
                <span style="color: #28a745;">Completed: {completed}</span> | 
                <span style="color: #ffc107;">Pending: {pending}</span>
            </div>
        """
        
        # Add todos
        for todo in self.todos:
            completed_class = "todo-completed" if todo["completed"] else ""
            toggle_text = "✓" if not todo["completed"] else "↶"
            toggle_class = "completed" if todo["completed"] else ""
            
            html += f"""
            <div class="todo-item {completed_class}">
                <div class="todo-text">{todo["text"]}</div>
                <div class="todo-actions">
                    <span style="font-size: 12px; color: #6c757d;">{todo["created_at"]}</span>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def get_todo_list_for_editing(self) -> List[Tuple[int, str, bool]]:
        """Get todos in a format suitable for editing"""
        return [(todo["id"], todo["text"], todo["completed"]) for todo in self.todos]

# Initialize the todo app
todo_app = TodoApp()

def add_todo_handler(text):
    display, error = todo_app.add_todo(text)
    return display, "", error if error else "Todo added successfully!"

def toggle_todo_handler(todo_id):
    if todo_id is not None:
        display = todo_app.toggle_todo(int(todo_id))
        return display, "Todo status updated!"
    return todo_app.get_todos_display(), "Please enter a valid todo ID"

def delete_todo_handler(todo_id):
    if todo_id is not None:
        display = todo_app.delete_todo(int(todo_id))
        return display, "Todo deleted!"
    return todo_app.get_todos_display(), "Please enter a valid todo ID"

def edit_todo_handler(todo_id, new_text):
    if todo_id is not None and new_text:
        display = todo_app.edit_todo(int(todo_id), new_text)
        return display, "", "Todo updated!"
    return todo_app.get_todos_display(), "", "Please enter valid todo ID and text"

def clear_completed_handler():
    display = todo_app.clear_completed()
    return display, "Completed todos cleared!"

# Create the Gradio interface
with gr.Blocks(title="Todo List App", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 📝 Todo List App")
    gr.Markdown("*A simple todo list built with Gradio*")
    
    with gr.Row():
        with gr.Column(scale=3):
            todo_input = gr.Textbox(
                placeholder="Enter a new todo...", 
                label="Add New Todo",
                lines=1
            )
        with gr.Column(scale=1):
            add_btn = gr.Button("Add Todo", variant="primary")
    
    message = gr.Textbox(label="Status", interactive=False, visible=False)
    
    todos_display = gr.HTML(value=todo_app.get_todos_display(), label="Your Todos")
    
    with gr.Accordion("Todo Actions", open=False):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Toggle/Delete Todo")
                action_id = gr.Number(label="Todo ID", precision=0)
                with gr.Row():
                    toggle_btn = gr.Button("Toggle Complete", size="sm")
                    delete_btn = gr.Button("Delete", size="sm", variant="stop")
            
            with gr.Column():
                gr.Markdown("### Edit Todo")
                edit_id = gr.Number(label="Todo ID to Edit", precision=0)
                edit_text = gr.Textbox(label="New Text", placeholder="Enter new todo text...")
                edit_btn = gr.Button("Update Todo", size="sm")
    
    with gr.Row():
        clear_btn = gr.Button("Clear Completed", variant="secondary")
        refresh_btn = gr.Button("Refresh", variant="secondary")
    
    status_msg = gr.Textbox(label="Status", interactive=False)
    
    # Event handlers
    add_btn.click(
        fn=add_todo_handler,
        inputs=[todo_input],
        outputs=[todos_display, todo_input, status_msg]
    )
    
    todo_input.submit(
        fn=add_todo_handler,
        inputs=[todo_input],
        outputs=[todos_display, todo_input, status_msg]
    )
    
    toggle_btn.click(
        fn=toggle_todo_handler,
        inputs=[action_id],
        outputs=[todos_display, status_msg]
    )
    
    delete_btn.click(
        fn=delete_todo_handler,
        inputs=[action_id],
        outputs=[todos_display, status_msg]
    )
    
    edit_btn.click(
        fn=edit_todo_handler,
        inputs=[edit_id, edit_text],
        outputs=[todos_display, edit_text, status_msg]
    )
    
    clear_btn.click(
        fn=clear_completed_handler,
        outputs=[todos_display, status_msg]
    )
    
    refresh_btn.click(
        fn=lambda: (todo_app.get_todos_display(), "Refreshed!"),
        outputs=[todos_display, status_msg]
    )

if __name__ == "__main__":
    app.launch(debug=True, share=True)