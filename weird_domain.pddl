(define (domain weirdness)
  (:requirements :adl :typing)
  (:types A B - C
         )

(:predicates 
(on ?obj - C)
(linked ?obj1 ?obj2 - C)
)


(:action turnon
  :parameters (?c - C)
  :precondition (not (on ?c))
  :effect (and (on ?c)
               (forall (?o - A) 
                  (when (and (linked ?c ?o) (not (on ?o)))
                        (on ?o)))
               (forall (?o - A) 
                  (when (and (linked ?c ?o) (on ?o))
                        (not (on ?o))))
               (forall (?o - B) 
                  (when (and (linked ?o ?c) (on ?o))
                        (not (on ?o))))
               (forall (?o - B) 
                  (when (and (linked ?o ?c) (not (on ?o)))
                        (on ?o)))
          )
               
)

)



