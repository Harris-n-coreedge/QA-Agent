"""
Utility functions for parsing browser-use agent history into structured output.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

# Try to import schemas, but don't fail if not available
try:
    from qa_agent.schemas import (
        ActionResult,
        ModelAction,
        NavigateAction,
        ClickAction,
        InputAction,
        ExtractAction,
        DoneAction,
        DOMInteractedElement,
        DOMRect,
        ActionHistory,
        StructuredAgentHistory,
    )
except (ImportError, NameError):
    # Define minimal fallback if schemas not available
    # These are only needed for the complex parser, not the simple one
    ActionResult = None
    ModelAction = None
    ActionHistory = None
    StructuredAgentHistory = None
    DOMInteractedElement = None
    DOMRect = None


def format_terminal_output_simple(history, task: str) -> str:
    """
    Parse and format agent history into a structured, story-like output.
    This is a direct implementation that works with the actual browser-use format.
    """
    lines = []
    lines.append(f"═══════════════════════════════════════════════════════")
    lines.append(f"  TEST EXECUTION SUMMARY")
    lines.append(f"═══════════════════════════════════════════════════════")
    lines.append(f"")
    lines.append(f"Task: {task}")
    lines.append(f"")
    
    # Get the string representation
    history_str = str(history)
    
    import re
    
    try:
        # Extract all_results section - use non-greedy with proper boundaries
        # Look for the pattern: all_results=[ stuff ]
        all_results_match = re.search(r'all_results=\[', history_str)
        
        if not all_results_match:
            lines.append("No execution history found.")
            lines.append("")
            lines.append("═══════════════════════════════════════════════════════")
            return "\n".join(lines)
        
        # Find all instances of ActionResult(
        results_start = all_results_match.end()
        
        # Find all ActionResult entries
        results_end = history_str.find('], all_model_outputs=', results_start)
        if results_end == -1:
            results_end = history_str.find('\n', results_start + 50000)  # Look for newline if no separator
        
        if results_end == -1 or results_end < results_start:
            results_end = len(history_str)
        
        results_content = history_str[results_start:results_end]

        # Also capture all_model_outputs section so we can get full 'done.text' (untruncated)
        model_outputs_content = ""
        mo_start = history_str.find('all_model_outputs=[', results_end)
        if mo_start != -1:
            # Find the closing ']' for the model outputs list
            pos = mo_start + len('all_model_outputs=[')
            depth = 1
            while pos < len(history_str):
                ch = history_str[pos]
                if ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
                    if depth == 0:
                        model_outputs_content = history_str[mo_start + len('all_model_outputs=['):pos]
                        break
                pos += 1
        
        # Parse individual ActionResult entries
        # First, find all ActionResult start positions
        action_results = []
        i = 0
        while i < len(results_content):
            # Look for "ActionResult("
            start = results_content.find("ActionResult(", i)
            if start == -1:
                break
            
            # Find matching closing parenthesis by tracking depth
            depth = 0
            pos = start + len("ActionResult(")
            paren_start = start + len("ActionResult")
            
            while pos < len(results_content):
                char = results_content[pos]
                
                # Track depth for nested parentheses
                if char == '(':
                    depth += 1
                elif char == ')':
                    if depth == 0:
                        # Found the matching closing paren for ActionResult
                        action_results.append(results_content[start:pos+1])
                        i = pos + 1
                        break
                    else:
                        depth -= 1
                
                pos += 1
            else:
                # Reached end without finding matching paren
                if start != -1:
                    # Take everything from start to end as a fallback
                    action_results.append(results_content[start:])
                break
        
        step_num = 1
        final_status = None
        test_passed = False
        
        for result in action_results:
            # Skip results that are just error markers
            if 'error="' in result and 'validation' in result.lower():
                continue
            
            # Extract fields using a more robust approach that handles multi-line strings
            def extract_field(result_str, field_name):
                # Look for field_name= pattern
                field_pattern = f"{field_name}="
                start_idx = result_str.find(field_pattern)
                if start_idx == -1:
                    return None
                
                # Move past the = sign
                start_idx += len(field_pattern)
                
                # Check what comes after =
                char = result_str[start_idx] if start_idx < len(result_str) else ''
                
                if char == "'" or char == '"':
                    # Quoted string - find matching quote
                    quote = char
                    start_idx += 1  # Move past opening quote
                    value = ""
                    pos = start_idx
                    in_escape = False
                    found_end = False
                    
                    # Look ahead to find the closing quote that's not escaped
                    while pos < len(result_str):
                        current_char = result_str[pos]
                        
                        if in_escape:
                            # Previous char was escape
                            value += current_char
                            in_escape = False
                        elif current_char == '\\':
                            # Escape next char
                            in_escape = True
                            value += current_char  # Keep the escape char
                        elif current_char == quote and not in_escape:
                            # Found the ending quote (not escaped)
                            found_end = True
                            break
                        else:
                            value += current_char
                        
                        pos += 1
                    
                    # If we didn't find the end, return what we have
                    if not found_end:
                        # Try to find any non-empty content
                        if value.strip():
                            return value.strip()
                        return None
                    
                    return value
                elif char == '[':
                    # List/Array
                    return None  # Skip for now
                elif char == '{':
                    # Dictionary
                    return None  # Will handle metadata separately
                else:
                    # Try to extract until comma or closing paren
                    value = ""
                    pos = start_idx
                    while pos < len(result_str) and result_str[pos] not in [',', ')']:
                        value += result_str[pos]
                        pos += 1
                    return value.strip()
            
            long_term_memory = extract_field(result, "long_term_memory")
            extracted_content = extract_field(result, "extracted_content")
            error_val = extract_field(result, "error")
            success_val = extract_field(result, "success")
            is_done_val = extract_field(result, "is_done")
            
            # Parse metadata separately since it's a dict
            metadata_match = re.search(r"metadata=\{(.*?)\}", result, re.DOTALL)
            
            # Extract metadata positions
            click_pos = None
            input_pos = None
            if metadata_match:
                meta_content = metadata_match.group(1)
                click_match = re.search(r"'click_x':\s*([0-9.]+).*?'click_y':\s*([0-9.]+)", meta_content)
                input_match = re.search(r"'input_x':\s*([0-9.]+).*?'input_y':\s*([0-9.]+)", meta_content)
                if click_match:
                    click_pos = (click_match.group(1), click_match.group(2))
                if input_match:
                    input_pos = (input_match.group(1), input_match.group(2))
            
            # Get action description and result text
            # Handle both single and double-quoted strings
            if long_term_memory:
                action_text = long_term_memory
            else:
                action_text = None
            
            if extracted_content:
                result_text = extracted_content
            else:
                result_text = None
            
            # Show steps if they have: action, result, error, or done status
            # This ensures failed test cases are still displayed
            has_content = (
                (action_text and action_text != 'None') or
                (result_text and result_text != 'None') or
                (error_val and error_val.strip() not in ['None', 'error']) or
                (is_done_val and is_done_val.strip() == 'True')
            )
            
            if has_content:
                lines.append(f"───────────────────────────────────────────────────────")
                lines.append(f"STEP {step_num}")
                lines.append(f"───────────────────────────────────────────────────────")
                lines.append("")
                
                # Show action if available, otherwise use result as action
                if action_text and action_text != 'None':
                    lines.append(f"Action: {action_text}")
                elif result_text and result_text != 'None':
                    lines.append(f"Action: {result_text}")
                else:
                    lines.append("Action: (No description)")
                lines.append("")
                
                # Show result if available and different from action
                if result_text and result_text != 'None' and result_text != action_text:
                    # Format XML-like content
                    if '<url>' in result_text or '<query>' in result_text or '<result>' in result_text:
                        lines.append("Extracted Information:")
                        for line in result_text.split('\n'):
                            line = line.strip()
                            if line:
                                lines.append(f"  {line}")
                    else:
                        lines.append(f"Result: {result_text}")
                    lines.append("")
                
                # Show positions if available
                if click_pos:
                    lines.append(f"📍 Click Position: ({click_pos[0]}, {click_pos[1]})")
                    lines.append("")
                
                if input_pos:
                    lines.append(f"⌨️  Input Position: ({input_pos[0]}, {input_pos[1]})")
                    lines.append("")
                
                # Show status
                if success_val and success_val.strip() != 'None':
                    status = "✅ SUCCESS" if success_val.strip() == 'True' else "❌ FAILED"
                    lines.append(f"Status: {status}")
                    lines.append("")
                    final_status = status
                    test_passed = (success_val.strip() == 'True')
                
                # Show errors - make them prominent for failed test cases
                if error_val and error_val.strip() != 'None' and error_val.strip() != 'error':
                    # Skip validation errors
                    if 'validation' not in error_val.lower() and 'error=' not in error_val:
                        error_msg = error_val.strip()
                        # Truncate long errors
                        if len(error_msg) > 500:
                            error_msg = error_msg[:500] + "... (truncated)"
                        lines.append(f"⚠️  ERROR:")
                        lines.append(f"   {error_msg}")
                        lines.append("")
                
                # Check if task is done
                if is_done_val and is_done_val.strip() == 'True':
                    lines.append("✓ TASK COMPLETED")
                    lines.append("")
                
                step_num += 1
        
        # Add final summary
        lines.append("")
        lines.append("───────────────────────────────────────────────────────")
        lines.append("TEST SUMMARY")
        lines.append("───────────────────────────────────────────────────────")
        lines.append("")
        
        # Extract final result if available
        # Prefer the full 'done.text' from all_model_outputs (not truncated),
        # otherwise fall back to long_term_memory that contains "Task completed".
        done_text = None
        done_success = None
        if model_outputs_content:
            # Extract last done.text
            dt_matches = re.findall(r"'done':\s*\{[^}]*'text':\s*(['\"])(.*?)\1", model_outputs_content, re.DOTALL)
            if dt_matches:
                done_text = dt_matches[-1][1]
                # Unescape common sequences
                done_text = done_text.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
            # Extract done.success
            ds_matches = re.findall(r"'done':\s*\{[^}]*'success':\s*(True|False)", model_outputs_content)
            if ds_matches:
                done_success = (ds_matches[-1] == 'True')

        # Look for both "Task completed" and error patterns in long_term_memory
        final_result_match = re.search(r"long_term_memory='[^']*Task completed[^']{0,500}'", history_str)
        
        # Also check for errors in the history
        error_in_history = re.search(r"error=[^,]*[^None]", history_str)
        
        final_text = None
        if final_result_match:
            final_text = final_result_match.group(0).replace("long_term_memory='", "").replace("'", "")
        
        # Prefer done_text if it's longer or if long_term_memory was not found
        if done_text and (final_text is None or len(done_text) > len(final_text) or 'more characters' in final_text if final_text else False):
            final_text = done_text
        
        # Extract the conclusion
        if final_text:
            # First check for failure indicators (more comprehensive detection)
            # Use case-insensitive regex to catch variations
            failure_patterns = [
                r"Test case is FAILED",
                r"test case is \*\*failed\*\*",
                r"Conclusion:\s*Test case failed",
                r"Conclusion:.*[Tt]est case failed",
                r"Test case failed",  # Simple explicit pattern
                r"does not match",
                r"not match",
                r"mismatch"
            ]
            
            # Check if any failure pattern matches (case-insensitive)
            has_failure_indicators = any(
                re.search(pattern, final_text, re.IGNORECASE) for pattern in failure_patterns
            ) or done_success is False
            
            # Then check for pass indicators (only explicit statements, no "consider/considered")
            pass_patterns = [
                r"Test case is PASSED",
                r"test case is \*\*passed\*\*",
                r"Conclusion:\s*Test case passed",
                r"Conclusion:.*[Tt]est case passed",
                r"Test case passed"  # Simple explicit pattern
            ]
            
            has_pass_indicators = (
                any(re.search(pattern, final_text, re.IGNORECASE) for pattern in pass_patterns) or
                done_success is True
            )
            
            # Prioritize failure detection - conclusion text takes priority over success flags
            if has_failure_indicators and not has_pass_indicators:
                lines.append("✗ TEST CASE STATUS: FAILED")
                test_passed = False
            elif has_pass_indicators and not has_failure_indicators:
                lines.append("✓ TEST CASE STATUS: PASSED")
                test_passed = True
            elif has_pass_indicators and has_failure_indicators:
                # If both are present, failure takes priority
                lines.append("✗ TEST CASE STATUS: FAILED")
                test_passed = False
            else:
                # If no clear conclusion in final_text, check if we have conclusion pattern
                # This handles cases where conclusion appears but wasn't caught by patterns above
                if re.search(r"Conclusion:.*failed", final_text, re.IGNORECASE):
                    lines.append("✗ TEST CASE STATUS: FAILED")
                    test_passed = False
                elif final_status:
                    lines.append(f"TEST STATUS: {final_status}")
            
            lines.append("")
            lines.append("Final Result:")
            lines.append("")
            
            # Show the final conclusion in a readable format
            if "1." in final_text and "2." in final_text:
                for line in final_text.split('\n'):
                    line = line.strip()
                    if line and line != 'Task completed: True':
                        lines.append(f"  {line}")
            else:
                lines.append(f"  {final_text}")
        elif (error_in_history and not test_passed) or (done_success is False):
            # If there was an error and test didn't pass, mark as failed
            lines.append("✗ TEST CASE STATUS: FAILED")
            lines.append("")
            lines.append("Error occurred during test execution.")
        elif test_passed:
            lines.append("✓ TEST CASE: PASSED")
        elif final_status:
            lines.append(f"TEST STATUS: {final_status}")
        else:
            # Check if we have any steps
            if step_num > 1:
                lines.append("⚠️  TEST CASE: UNKNOWN STATUS")
            else:
                lines.append("⚠️  No test execution data available")
        
        lines.append("")
        
    except Exception as e:
        # If parsing fails, show at least a formatted version of raw output
        lines.append(f"⚠️  Parsing encountered an error: {str(e)}")
        lines.append("")
        lines.append("───────────────────────────────────────────────────────")
        lines.append("SHOWING RAW OUTPUT")
        lines.append("───────────────────────────────────────────────────────")
        lines.append("")
        
        # Show the first part of the raw output
        raw_output = str(history)[:1500]  # First 1500 chars
        lines.append(raw_output)
        if len(str(history)) > 1500:
            lines.append("")
            lines.append("... (truncated)")
    
    # Ensure we always return something meaningful
    if len(lines) <= 10:  # If we barely added anything, provide fallback
        lines = []
        lines.append(f"═══════════════════════════════════════════════════════")
        lines.append(f"  TEST EXECUTION HISTORY")
        lines.append(f"═══════════════════════════════════════════════════════")
        lines.append(f"")
        lines.append(f"Task: {task}")
        lines.append("")
        lines.append("Note: Detailed parsing unavailable. Showing raw output:")
        lines.append("")
        lines.append(str(history)[:2000])
    
    lines.append(f"")
    lines.append(f"═══════════════════════════════════════════════════════")
    
    return "\n".join(lines)


def format_terminal_output(history, task: str) -> str:
    """
    Format agent history into a terminal-style readable output.
    This creates a structured text representation of the execution.
    """
    lines = []
    lines.append(f"═══════════════════════════════════════════════════════")
    lines.append(f"  AGENT EXECUTION HISTORY")
    lines.append(f"═══════════════════════════════════════════════════════")
    lines.append(f"")
    lines.append(f"Task: {task}")
    lines.append(f"")
    
    try:
        # Try to get structured data from history
        all_results = []
        all_model_outputs = []
        
        if hasattr(history, 'action_results'):
            try:
                all_results = history.action_results()
            except:
                pass
        
        if hasattr(history, 'model_outputs'):
            try:
                all_model_outputs = history.model_outputs()
            except:
                pass
        
        # If we have structured data, process it
        if all_results and len(all_results) > 0:
            # Process each step
            for idx, result_data in enumerate(all_results, 1):
                lines.append(f"───────────────────────────────────────────────────────")
                lines.append(f"STEP {idx}")
                lines.append(f"───────────────────────────────────────────────────────")
                
                # Show action result information
                if hasattr(result_data, 'long_term_memory') and result_data.long_term_memory:
                    lines.append(f"Action: {result_data.long_term_memory}")
                
                if hasattr(result_data, 'extracted_content') and result_data.extracted_content:
                    lines.append(f"Result: {result_data.extracted_content}")
                
                if hasattr(result_data, 'metadata') and result_data.metadata:
                    metadata = result_data.metadata
                    if 'click_x' in metadata and 'click_y' in metadata:
                        lines.append(f"Click Position: ({metadata['click_x']}, {metadata['click_y']})")
                    if 'input_x' in metadata and 'input_y' in metadata:
                        lines.append(f"Input Position: ({metadata['input_x']}, {metadata['input_y']})")
                
                # Show status
                if hasattr(result_data, 'success') and result_data.success is not None:
                    status = "✓ SUCCESS" if result_data.success else "✗ FAILED"
                    lines.append(f"Status: {status}")
                
                if hasattr(result_data, 'error') and result_data.error:
                    lines.append(f"Error: {result_data.error}")
                
                if hasattr(result_data, 'is_done') and result_data.is_done:
                    lines.append(f"Task Complete: True")
                
                lines.append("")
            
            # Add summary
            visited_urls = []
            final_result = None
            
            if hasattr(history, 'urls'):
                try:
                    visited_urls = history.urls()
                except:
                    pass
            
            if hasattr(history, 'final_result'):
                try:
                    final_result = history.final_result()
                except:
                    pass
            
            if visited_urls:
                lines.append("───────────────────────────────────────────────────────")
                lines.append("VISITED URLs")
                lines.append("───────────────────────────────────────────────────────")
                for url in visited_urls:
                    lines.append(f"  • {url}")
                lines.append("")
            
            if final_result:
                lines.append("───────────────────────────────────────────────────────")
                lines.append("FINAL RESULT")
                lines.append("───────────────────────────────────────────────────────")
                lines.append(final_result)
        else:
            # Fallback: parse the string representation
            history_str = str(history)
            
            # Remove validation errors from output
            import re
            
            # Find all ActionResult entries and extract their content
            # Look for the pattern: long_term_memory='...'
            action_matches = re.finditer(r"(?:long_term_memory|extracted_content)=('(?:[^'\\]|\\.)*')", history_str)
            
            step_num = 1
            current_step_data = {}
            
            for match in action_matches:
                field = match.string[match.start():match.start() + match.group().find('=')]
                value = match.group(1).strip("'")
                
                # Track the current step
                if 'long_term_memory' in field and value and not value.startswith('Task completed'):
                    if current_step_data:
                        # Output previous step
                        lines.append(f"───────────────────────────────────────────────────────")
                        lines.append(f"STEP {step_num}")
                        lines.append(f"───────────────────────────────────────────────────────")
                        
                        if 'action' in current_step_data:
                            lines.append(f"Action: {current_step_data['action']}")
                        if 'result' in current_step_data:
                            lines.append(f"Result: {current_step_data['result']}")
                        if 'metadata' in current_step_data:
                            meta = current_step_data['metadata']
                            if 'click_x' in meta:
                                lines.append(f"Click Position: ({meta['click_x']}, {meta['click_y']})")
                            if 'input_x' in meta:
                                lines.append(f"Input Position: ({meta['input_x']}, {meta['input_y']})")
                        lines.append("")
                        step_num += 1
                    
                    current_step_data = {'action': value}
                
                elif 'extracted_content' in field and value:
                    current_step_data['result'] = value
            
            # Output the last step if exists
            if current_step_data:
                lines.append(f"───────────────────────────────────────────────────────")
                lines.append(f"STEP {step_num}")
                lines.append(f"───────────────────────────────────────────────────────")
                
                if 'action' in current_step_data:
                    lines.append(f"Action: {current_step_data['action']}")
                if 'result' in current_step_data:
                    lines.append(f"Result: {current_step_data['result']}")
                lines.append("")
            
            # Find final result at the end
            final_match = re.search(r"Task completed:\s*True\s*-\s*([^\n]+)", history_str)
            if final_match:
                lines.append("───────────────────────────────────────────────────────")
                lines.append("FINAL RESULT")
                lines.append("───────────────────────────────────────────────────────")
                lines.append(f"Task completed: {final_match.group(1).strip()}")
                lines.append("")
        
    except Exception as e:
        lines.append(f"Error formatting history: {str(e)}")
        lines.append(f"\nUnable to format output properly.")
    
    lines.append(f"")
    lines.append(f"═══════════════════════════════════════════════════════")
    
    return "\n".join(lines)


def _get_action_info(model_output: Dict[str, Any]) -> str:
    """Extract human-readable action info from model output."""
    if 'navigate' in model_output:
        url = model_output['navigate'].get('url', '')
        return f"Navigate to: {url}"
    elif 'click' in model_output:
        index = model_output['click'].get('index', 0)
        return f"Click element at index: {index}"
    elif 'input' in model_output:
        index = model_output['input'].get('index', 0)
        text = model_output['input'].get('text', '')[:50]
        return f"Input into element {index}: '{text}'"
    elif 'extract' in model_output:
        query = model_output['extract'].get('query', '')[:50]
        return f"Extract: '{query}'"
    elif 'done' in model_output:
        text = model_output['done'].get('text', '')[:50]
        return f"Done: '{text}'"
    return None


def parse_agent_history(
    history,
    task: str,
    status: str = "completed"
):
    """
    Parse agent history - DISABLED to avoid schema dependencies.
    Use format_terminal_output_simple instead.
    This function returns None to avoid calling Pydantic schemas that may not be available.
    """
    return None


def parse_agent_history_original(
    history,
    task: str,
    status: str = "completed"
):
    """
    Original parse function - DISABLED due to schema dependencies.
    """
    try:
        # Get all model outputs and action results
        all_results = history.action_results() if hasattr(history, 'action_results') else []
        all_model_outputs = history.model_outputs() if hasattr(history, 'model_outputs') else []
        
        # Parse actions
        actions = []
        for idx, (result_data, model_output) in enumerate(zip(all_results, all_model_outputs)):
            # Parse ActionResult
            action_result = ActionResult(
                is_done=result_data.is_done if hasattr(result_data, 'is_done') else False,
                success=result_data.success if hasattr(result_data, 'success') else None,
                error=result_data.error if hasattr(result_data, 'error') else None,
                attachments=result_data.attachments if hasattr(result_data, 'attachments') else [],
                long_term_memory=result_data.long_term_memory if hasattr(result_data, 'long_term_memory') else None,
                extracted_content=result_data.extracted_content if hasattr(result_data, 'extracted_content') else None,
                include_extracted_content_only_once=result_data.include_extracted_content_only_once if hasattr(result_data, 'include_extracted_content_only_once') else False,
                metadata=result_data.metadata if hasattr(result_data, 'metadata') else None,
                include_in_memory=result_data.include_in_memory if hasattr(result_data, 'include_in_memory') else False,
            )
            
            # Parse model action
            model_action = None
            if model_output:
                model_action = _parse_model_action(model_output, result_data)
            
            actions.append(ActionHistory(
                action_result=action_result,
                model_action=model_action,
                step_number=idx + 1
            ))
        
        # Get additional data from history
        visited_urls = history.urls() if hasattr(history, 'urls') else []
        extracted_content = history.extracted_content() if hasattr(history, 'extracted_content') else []
        errors = [e for e in history.errors() if e] if hasattr(history, 'errors') else []
        final_result = history.final_result() if hasattr(history, 'final_result') else None
        is_done = history.is_done() if hasattr(history, 'is_done') else False
        is_successful = history.is_successful() if hasattr(history, 'is_successful') else None
        has_errors = history.has_errors() if hasattr(history, 'has_errors') else len(errors) > 0
        
        return StructuredAgentHistory(
            task=task,
            status=status,
            total_steps=len(actions),
            actions=actions,
            visited_urls=visited_urls,
            extracted_content=extracted_content,
            errors=errors,
            final_result=final_result,
            is_done=is_done,
            is_successful=is_successful,
            has_errors=has_errors,
            executed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        # Return minimal structure on parsing error
        return StructuredAgentHistory(
            task=task,
            status="error",
            total_steps=0,
            actions=[],
            visited_urls=[],
            extracted_content=[],
            errors=[f"Failed to parse agent history: {str(e)}"],
            final_result=None,
            is_done=False,
            is_successful=False,
            has_errors=True,
            executed_at=datetime.utcnow().isoformat()
        )


def _parse_model_action(model_output: Dict[str, Any], result_data) -> Optional[ModelAction]:
    """
    Parse a model output dictionary into a ModelAction object.
    """
    try:
        action_type = None
        navigate = None
        click = None
        input_action = None
        extract = None
        done = None
        interacted_element = None
        
        # Determine action type
        if 'navigate' in model_output:
            action_type = "navigate"
            nav_data = model_output['navigate']
            navigate = NavigateAction(
                url=nav_data.get('url', ''),
                new_tab=nav_data.get('new_tab', False)
            )
            
        elif 'click' in model_output:
            action_type = "click"
            click_data = model_output['click']
            click = ClickAction(index=click_data.get('index', 0))
            
        elif 'input' in model_output:
            action_type = "input"
            input_data = model_output['input']
            input_action = InputAction(
                index=input_data.get('index', 0),
                text=input_data.get('text', ''),
                clear=input_data.get('clear', True)
            )
            
        elif 'extract' in model_output:
            action_type = "extract"
            extract_data = model_output['extract']
            extract = ExtractAction(
                query=extract_data.get('query', ''),
                extract_links=extract_data.get('extract_links', False),
                start_from_char=extract_data.get('start_from_char', 0)
            )
            
        elif 'done' in model_output:
            action_type = "done"
            done_data = model_output['done']
            done = DoneAction(
                text=done_data.get('text', ''),
                success=done_data.get('success', True),
                files_to_display=done_data.get('files_to_display', [])
            )
        
        # Parse interacted element if present
        if 'interacted_element' in model_output and model_output['interacted_element']:
            interacted_element = _parse_interacted_element(model_output['interacted_element'])
        
        return ModelAction(
            action_type=action_type or "unknown",
            navigate=navigate,
            click=click,
            input=input_action,
            extract=extract,
            done=done,
            interacted_element=interacted_element
        )
        
    except Exception as e:
        # Return None if parsing fails
        return None


def _parse_interacted_element(element_data: Dict[str, Any]) -> DOMInteractedElement:
    """
    Parse an interacted element dictionary into a DOMInteractedElement object.
    """
    bounds_data = element_data.get('bounds', {})
    bounds = DOMRect(
        x=bounds_data.get('x', 0),
        y=bounds_data.get('y', 0),
        width=bounds_data.get('width', 0),
        height=bounds_data.get('height', 0)
    )
    
    return DOMInteractedElement(
        node_id=element_data.get('node_id', 0),
        backend_node_id=element_data.get('backend_node_id', 0),
        frame_id=element_data.get('frame_id'),
        node_type=element_data.get('node_type', ''),
        node_value=element_data.get('node_value', ''),
        node_name=element_data.get('node_name', ''),
        attributes=element_data.get('attributes', {}),
        bounds=bounds,
        x_path=element_data.get('x_path', ''),
        element_hash=element_data.get('element_hash', 0)
    )


def format_history_for_display(structured_history) -> Dict[str, Any]:
    """
    Format history for display - DISABLED to avoid schema dependencies.
    """
    if structured_history is None:
        return {"error": "History not available"}
    
    # Return minimal structure to avoid calling schema methods
    return {
        "task": "Unknown",
        "status": "unknown",
        "summary": {"total_steps": 0},
        "visited_urls": [],
        "final_result": None
    }


def format_history_for_display_original(structured_history) -> Dict[str, Any]:
    """
    Original format function - DISABLED due to schema dependencies.
    """
    return {
        "task": structured_history.task,
        "status": structured_history.status,
        "summary": {
            "total_steps": structured_history.total_steps,
            "visited_urls_count": len(structured_history.visited_urls),
            "has_errors": structured_history.has_errors,
            "is_successful": structured_history.is_successful,
            "is_done": structured_history.is_done,
        },
        "visited_urls": structured_history.visited_urls,
        "final_result": structured_history.final_result,
        "actions_summary": [
            {
                "step": action.step_number,
                "action_type": action.model_action.action_type if action.model_action else "unknown",
                "extracted_content": action.action_result.extracted_content,
                "error": action.action_result.error,
                "success": action.action_result.success,
            }
            for action in structured_history.actions
        ],
        "executed_at": structured_history.executed_at,
    }

