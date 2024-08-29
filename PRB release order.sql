SELECT
    ROW_NUMBER() OVER(ORDER BY prb_cred, prb_cret) AS sequence,
    prb_prjc,
    prb_seqn
FROM
    (
        SELECT
            prb_prjc,
            prb_seqn,
            prb_cred,
            prb_cret,
            ROW_NUMBER() OVER (PARTITION BY prb_prjc ORDER BY prb_cred DESC, prb_cret DESC) AS ranked_order
        FROM
            men_prb
    )
WHERE
    prb_prjc IN (
        '…', '…'
    )
    AND ranked_order = 1
order by
    prb_cred,
    prb_cret
