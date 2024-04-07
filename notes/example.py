"""
In this file there is an example of knowledge graph.
This is used to kick-start new knowledge graph.
Users and AI needs something to not get confused,
but later they may change the structure and nature of given instance 100%.
"""


content_scientific_method = ''' \
The scientific method is a systematic process for investigating the world around us. \
It involves the following steps:
Observation: Identify a question or phenomenon to explore.
Hypothesis: Formulate a testable explanation.
Experimentation: Design and conduct experiments to gather data.
Analysis: Examine the data to draw conclusions.
Conclusion: Support or reject the hypothesis, refine the question.
'''

content_newtons_laws = ''' \
1st Law (Inertia): An object at rest stays at rest, and an object in motion \
stays in motion unless acted on by an outside force.
2nd Law (F=ma): The force acting on an object is equal to the object's mass times its acceleration.
3rd Law (Action-Reaction): For every action, there is an equal and opposite reaction.
'''

content_cognitive_biases = ''' \
Our minds unconsciously take shortcuts in how we process information. These shortcuts, called cognitive biases, \
can lead to flawed thinking. Common examples include:
Confirmation bias: Seeking information that confirms existing beliefs.
Availability bias: Overestimating the importance of information that's easily recalled.
'''

content_baking_cake = ''' \
Basic Cake Recipe

Ingredients:
1 cup all-purpose flour
1 tsp baking powder
1/2 cup sugar
1 stick butter (softened)
2 eggs
1 tsp vanilla extract

Instructions:
Preheat oven to 350 degrees.
Mix dry ingredients.
Cream together butter and sugar, then add eggs and vanilla.
Gradually add dry mix to wet mix.
Pour into greased pan, bake 30-35 minutes
'''

example_notes = {
    1: {
        'content': content_scientific_method,
        'references': (2,),
    },
    2: {
        'content': content_newtons_laws,
        'references': (1,),
    },
    3: {
        'content': content_cognitive_biases,
        'references': (1, '3q'),
    },
    '3q': {
        'content': 'Does cognitive biases help sometimes?',
        'references': (),
    },
    4: {
        'content': content_baking_cake,
        'references': (),
    },
    5: {
        'content': "Why is the sky blue?",
        'references': (),
    },
}
