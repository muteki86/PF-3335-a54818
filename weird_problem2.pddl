(define (problem weird)
   (:domain weirdness)
   (:objects x y - A
             z w - B)


(:init

(linked y z)
(linked w x)
(linked x z)
(linked y w)
)


(:goal (forall (?o - C) (or (= ?o x) (on ?o))))

)


