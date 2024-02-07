CREATE TABLE public.candidates (
	candidate_id serial4 NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	link varchar NULL,
	CONSTRAINT candidates_pkey PRIMARY KEY (candidate_id)
);

CREATE TABLE public.black_list (
	black_list_id serial4 NOT NULL,
	candidate_id int4 NULL,
	CONSTRAINT black_list_pkey PRIMARY KEY (black_list_id)
);

ALTER TABLE public.black_list ADD CONSTRAINT black_list_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id);

CREATE TABLE public.favorite_list (
	favorite_list_id serial4 NOT NULL,
	candidate_id int4 NULL,
	CONSTRAINT favorite_list_pkey PRIMARY KEY (favorite_list_id)
);

ALTER TABLE public.favorite_list ADD CONSTRAINT favorite_list_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id);

CREATE TABLE public.photos (
	photos_id serial4 NOT NULL,
	photos_ids int4 NULL,
	candidate_id int4 NULL,
	CONSTRAINT photos_pkey PRIMARY KEY (photos_id)
);

ALTER TABLE public.photos ADD CONSTRAINT photos_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(candidate_id);