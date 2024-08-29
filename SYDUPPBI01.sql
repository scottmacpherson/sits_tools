SELECT * FROM (
    WITH ranked_men_prb AS (
        SELECT
            men_prb.prb_prjc,
            men_prb.prb_seqn,
            ROW_NUMBER() OVER (
                PARTITION BY
                    men_prb.prb_prjc
                ORDER BY
                    men_prb.prb_cred DESC,
                    men_prb.prb_cret DESC
            ) AS rn
        FROM
            men_prb
    ),
    men_pbi_for_latest_build_of_active_prjs AS (
        SELECT
            men_pbi.pbi_prjc,
            men_pbi.pbi_dctc,
            men_pbi.pbi_entc,
            men_pbi.pbi_pkvs,
            men_pbi.pbi_cred,
            men_pbi.pbi_cret
        FROM
            men_prj
            JOIN ranked_men_prb
                ON ranked_men_prb.prb_prjc = men_prj.prj_code
            JOIN men_pbi ON
                men_pbi.pbi_prjc = ranked_men_prb.prb_prjc
                AND men_pbi.pbi_prbs = ranked_men_prb.prb_seqn
        WHERE
            men_prj.prj_iuse = 'Y'
            AND men_prj.prj_actv = 'Y'
            AND ranked_men_prb.rn = 1
            AND men_pbi.pbi_dctc || '.' || men_pbi.pbi_entc NOT IN ('MENSYS.PRT', 'MENSYS.SLV')
    )
    SELECT
        -- The output of this SELECT is interpolated into a JavaScript string literal via the
        -- calling SRL. JSON_OBJECT correctly escapes double-quotes, but the backslash needs to be
        -- escaped again so it doesn't get eaten before being send to JSON.parse. Single quotes also
        -- need to be escaped so they don't interfere with the literal declaration. [headache emoji]
        REPLACE(
            REPLACE(
                JSON_OBJECT(
                    'Project code': men_pbi_for_latest_build_of_active_prjs.pbi_prjc,
                    'Project name': men_prj.prj_name,
                    'Duplicate project code': duplicate_men_pbi_for_latest_build_of_active_prjs.pbi_prjc,
                    'Build item created': TO_CHAR(men_pbi_for_latest_build_of_active_prjs.pbi_cred, 'YYYY-MM-DD') || 'T' || TO_CHAR(men_pbi_for_latest_build_of_active_prjs.pbi_cret, 'HH24:MI'),
                    'Dictonary': men_pbi_for_latest_build_of_active_prjs.pbi_dctc,
                    'Entity': men_pbi_for_latest_build_of_active_prjs.pbi_entc,
                    'Primary key': REPLACE(men_pbi_for_latest_build_of_active_prjs.pbi_pkvs, UNISTR('\001b'), ', ')
                ),
                '\"',
                '\\"'
            ),
            '''',
            '\'''
        )
    FROM
        men_prj
        JOIN men_pbi_for_latest_build_of_active_prjs
            ON men_pbi_for_latest_build_of_active_prjs.pbi_prjc = men_prj.prj_code
        JOIN men_pbi_for_latest_build_of_active_prjs duplicate_men_pbi_for_latest_build_of_active_prjs
            ON duplicate_men_pbi_for_latest_build_of_active_prjs.pbi_prjc != men_pbi_for_latest_build_of_active_prjs.pbi_prjc
            AND duplicate_men_pbi_for_latest_build_of_active_prjs.pbi_dctc = men_pbi_for_latest_build_of_active_prjs.pbi_dctc
            AND duplicate_men_pbi_for_latest_build_of_active_prjs.pbi_entc = men_pbi_for_latest_build_of_active_prjs.pbi_entc
            AND duplicate_men_pbi_for_latest_build_of_active_prjs.pbi_pkvs = men_pbi_for_latest_build_of_active_prjs.pbi_pkvs
)
