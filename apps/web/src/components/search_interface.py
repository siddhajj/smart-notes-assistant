import reflex as rx
from ..state.search_state import SearchState

def search_input() -> rx.Component:
    """Search input component for the bottom chat area"""
    return rx.box(
        rx.hstack(
            rx.input(
                placeholder="Ask a question or search for notes and tasks...",
                value=SearchState.search_query,
                on_change=SearchState.set_search_query,
                size="lg",
                flex="1",
                border_radius="full",
                padding_left="1rem",
                _focus={
                    "border_color": "blue.500",
                    "box_shadow": "0 0 0 1px var(--chakra-colors-blue-500)"
                }
            ),
            
            rx.button(
                rx.cond(
                    SearchState.search_loading,
                    rx.spinner(size="sm"),
                    rx.icon("search", size=20)
                ),
                on_click=lambda: SearchState.perform_search(SearchState.search_query),
                color_scheme="blue",
                size="lg",
                border_radius="full",
                padding="0 1.5rem",
                is_loading=SearchState.search_loading
            ),
            
            spacing="3",
            width="100%",
            align="center"
        ),
        
        width="100%",
        max_width="800px",
        margin="0 auto",
        padding="1rem"
    )

def rag_answer_panel() -> rx.Component:
    """RAG answer display panel"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading(
                    "AI Answer",
                    size="5",
                    color="gray.800",
                    weight="bold"
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("arrow-left", size=16),
                    "Back to Notes & Tasks",
                    on_click=SearchState.clear_search_results,
                    variant="outline",
                    size="sm",
                    color_scheme="gray"
                ),
                width="100%",
                align="center",
                margin_bottom="1rem"
            ),
            
            # Search query display
            rx.box(
                rx.text(
                    f"Query: {SearchState.search_query}",
                    font_size="0.9rem",
                    color="gray.600",
                    font_style="italic"
                ),
                padding="0.75rem",
                background="gray.100",
                border_radius="md",
                margin_bottom="1rem",
                width="100%"
            ),
            
            # RAG answer
            rx.cond(
                SearchState.search_loading,
                # Loading state
                rx.vstack(
                    rx.spinner(size="lg"),
                    rx.text("Searching and analyzing...", color="gray.500"),
                    align="center",
                    spacing="3",
                    padding="3rem"
                ),
                # Answer content
                rx.box(
                    rx.cond(
                        SearchState.rag_answer,
                        rx.vstack(
                            rx.text(
                                SearchState.rag_answer,
                                font_size="1rem",
                                line_height="1.6",
                                color="gray.800"
                            ),
                            
                            # Context indicator
                            rx.cond(
                                SearchState.context_used,
                                rx.hstack(
                                    rx.icon("check-circle", size=16, color="green.500"),
                                    rx.text(
                                        f"Answer based on {SearchState.total_results} relevant items from your notes and tasks",
                                        font_size="0.8rem",
                                        color="green.600"
                                    ),
                                    margin_top="1rem",
                                    spacing="2"
                                ),
                                rx.hstack(
                                    rx.icon("info", size=16, color="orange.500"),
                                    rx.text(
                                        "No relevant content found in your notes and tasks",
                                        font_size="0.8rem",
                                        color="orange.600"
                                    ),
                                    margin_top="1rem",
                                    spacing="2"
                                )
                            ),
                            
                            align="start",
                            spacing="2",
                            width="100%"
                        ),
                        rx.text(
                            "No answer available",
                            color="gray.500",
                            font_style="italic"
                        )
                    ),
                    
                    padding="1.5rem",
                    background="white",
                    border="1px solid",
                    border_color="gray.200",
                    border_radius="lg",
                    width="100%",
                    min_height="200px"
                )
            ),
            
            align="start",
            spacing="0",
            width="100%",
            height="100%"
        ),
        
        width="60%",
        height="100%",
        padding="1.5rem",
        border_right="1px solid var(--chakra-colors-gray-200)"
    )

def grounding_panel() -> rx.Component:
    """Grounding elements panel showing relevant notes and tasks"""
    return rx.box(
        rx.vstack(
            # Header
            rx.heading(
                "Relevant Content",
                size="5",
                color="gray.800",
                weight="bold",
                margin_bottom="1rem"
            ),
            
            # Results summary
            rx.cond(
                SearchState.total_results > 0,
                rx.text(
                    f"Found {SearchState.total_results} relevant items",
                    font_size="0.9rem",
                    color="gray.600",
                    margin_bottom="1rem"
                )
            ),
            
            # Results content
            rx.box(
                rx.vstack(
                    # Notes section
                    rx.cond(
                        SearchState.result_notes,
                        rx.vstack(
                            rx.text(
                                "Notes",
                                font_weight="semibold",
                                color="gray.700",
                                margin_bottom="0.5rem"
                            ),
                            rx.foreach(
                                SearchState.result_notes,
                                lambda result: grounding_note_item(result)
                            ),
                            width="100%",
                            spacing="2",
                            margin_bottom="1.5rem"
                        )
                    ),
                    
                    # Tasks section
                    rx.cond(
                        SearchState.result_tasks,
                        rx.vstack(
                            rx.text(
                                "Tasks",
                                font_weight="semibold",
                                color="gray.700",
                                margin_bottom="0.5rem"
                            ),
                            rx.foreach(
                                SearchState.result_tasks,
                                lambda result: grounding_task_item(result)
                            ),
                            width="100%",
                            spacing="2"
                        )
                    ),
                    
                    # No results
                    rx.cond(
                        (SearchState.total_results == 0) & ~SearchState.search_loading,
                        rx.center(
                            rx.vstack(
                                rx.icon("search", size=48, color="gray.400"),
                                rx.text(
                                    "No relevant content found",
                                    font_size="lg",
                                    color="gray.500",
                                    weight="semibold"
                                ),
                                rx.text(
                                    "Try a different search query",
                                    font_size="sm",
                                    color="gray.400"
                                ),
                                spacing="2",
                                align="center"
                            ),
                            padding="2rem"
                        )
                    ),
                    
                    width="100%",
                    spacing="0",
                    align="start"
                ),
                
                width="100%",
                height="100%",
                overflow_y="auto",
                max_height="calc(80vh - 120px)"
            ),
            
            align="start",
            spacing="0",
            width="100%",
            height="100%"
        ),
        
        width="40%",
        height="100%",
        padding="1.5rem"
    )

def grounding_note_item(result) -> rx.Component:
    """Individual note item in grounding panel"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    result.title,
                    font_weight="semibold",
                    color="gray.800",
                    font_size="0.95rem"
                ),
                rx.spacer(),
                rx.cond(
                    result.similarity_score,
                    rx.badge(
                        SearchState.get_similarity_percentage(result.similarity_score),
                        color_scheme="blue",
                        size="sm"
                    )
                ),
                width="100%",
                align="center"
            ),
            
            rx.text(
                SearchState.get_result_preview(result, 100),
                font_size="0.85rem",
                color="gray.600",
                line_height="1.4"
            ),
            
            rx.cond(
                result.tags,
                rx.wrap(
                    rx.foreach(
                        result.tags,
                        lambda tag: rx.badge(
                            tag,
                            color_scheme="gray",
                            size="sm",
                            variant="outline"
                        )
                    ),
                    spacing="0.25rem"
                )
            ),
            
            align="start",
            spacing="1",
            width="100%"
        ),
        
        on_click=lambda: SearchState.show_view_note_modal(result),
        cursor="pointer",
        padding="0.75rem",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
        background="white",
        _hover={
            "border_color": "blue.300",
            "shadow": "sm"
        },
        transition="all 0.2s ease",
        width="100%"
    )

def grounding_task_item(result) -> rx.Component:
    """Individual task item in grounding panel"""
    return rx.box(
        rx.hstack(
            rx.checkbox(
                is_checked=result.is_completed,
                on_change=lambda checked: SearchState.toggle_task_completion(result.id, checked),
                color_scheme="green",
                size="md"
            ),
            
            rx.vstack(
                rx.text(
                    result.title,
                    font_size="0.9rem",
                    color=rx.cond(result.is_completed, "gray.500", "gray.800"),
                    text_decoration=rx.cond(result.is_completed, "line-through", "none"),
                    weight="medium",
                    line_height="1.4"
                ),
                
                rx.hstack(
                    rx.cond(
                        result.similarity_score,
                        rx.badge(
                            SearchState.get_similarity_percentage(result.similarity_score),
                            color_scheme="blue",
                            size="sm"
                        )
                    ),
                    
                    rx.cond(
                        result.priority,
                        rx.badge(
                            result.priority.capitalize(),
                            color_scheme=SearchState.get_priority_color(result.priority),
                            size="sm"
                        )
                    ),
                    
                    spacing="2"
                ),
                
                align="start",
                spacing="1",
                flex="1"
            ),
            
            rx.icon_button(
                rx.icon("x", size=14),
                on_click=lambda: SearchState.delete_task(result.id),
                variant="ghost",
                color_scheme="red",
                size="sm"
            ),
            
            width="100%",
            align="start",
            spacing="2"
        ),
        
        padding="0.75rem",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
        background="white",
        _hover={"border_color": "gray.300"},
        transition="border-color 0.2s ease",
        width="100%"
    )

def search_results_view() -> rx.Component:
    """Complete search results view"""
    return rx.hstack(
        rag_answer_panel(),
        grounding_panel(),
        width="100%",
        height="80vh",
        spacing="0",
        align="start"
    )