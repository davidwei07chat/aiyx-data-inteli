create extension if not exists http with schema extensions;

create or replace function public.verify_wx_image_r2_assets_http_v1(
  p_limit integer default 100
)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_asset record;
  v_response extensions.http_response;
  v_checked integer := 0;
  v_verified integer := 0;
  v_missing integer := 0;
  v_error integer := 0;
  v_status integer;
  v_content_type text;
  v_error_message text;
begin
  if coalesce(p_limit, 0) < 1 then
    return jsonb_build_object(
      'ok', true,
      'checked', 0,
      'verified', 0,
      'missing', 0,
      'error', 0
    );
  end if;

  perform set_config('http.curlopt_connecttimeout_ms', '5000', true);
  perform set_config('http.curlopt_timeout_ms', '15000', true);
  perform set_config('http.curlopt_followlocation', '1', true);

  for v_asset in
    select a.image_md5, a.r2_url
    from public.wx_image_assets a
    where a.upload_status in ('uploaded', 'exists')
      and a.r2_key is not null
      and a.r2_url is not null
      and (
        a.r2_verified_at is null
        or a.r2_verify_status in ('missing', 'error')
      )
    order by a.r2_verified_at asc nulls first, a.updated_at asc, a.image_md5
    limit p_limit
    for update skip locked
  loop
    v_checked := v_checked + 1;
    v_status := null;
    v_content_type := null;
    v_error_message := null;

    begin
      v_response := extensions.http_head(v_asset.r2_url::varchar);
      v_status := v_response.status;
      v_content_type := nullif(btrim(v_response.content_type), '');

      if v_status between 200 and 399 then
        update public.wx_image_assets
        set
          r2_verify_status = 'verified',
          r2_verified_at = now(),
          r2_last_error = null,
          mime_type = coalesce(v_content_type, mime_type),
          image_status = 'active',
          r2_check_locked_at = null,
          r2_check_locked_by = null,
          updated_at = now()
        where image_md5 = v_asset.image_md5;
        v_verified := v_verified + 1;

      elsif v_status = 404 then
        update public.wx_image_assets
        set
          r2_verify_status = 'missing',
          r2_verified_at = now(),
          r2_last_error = 'R2 object returned HTTP 404',
          image_status = 'missing',
          r2_check_locked_at = null,
          r2_check_locked_by = null,
          updated_at = now()
        where image_md5 = v_asset.image_md5;
        v_missing := v_missing + 1;

      else
        v_error_message := format('R2 HEAD returned HTTP %s', coalesce(v_status::text, 'unknown'));
        update public.wx_image_assets
        set
          r2_verify_status = 'error',
          r2_verified_at = now(),
          r2_last_error = v_error_message,
          r2_check_locked_at = null,
          r2_check_locked_by = null,
          updated_at = now()
        where image_md5 = v_asset.image_md5;
        v_error := v_error + 1;
      end if;

    exception when others then
      v_error_message := left(sqlerrm, 1500);
      update public.wx_image_assets
      set
        r2_verify_status = 'error',
        r2_verified_at = now(),
        r2_last_error = v_error_message,
        r2_check_locked_at = null,
        r2_check_locked_by = null,
        updated_at = now()
      where image_md5 = v_asset.image_md5;
      v_error := v_error + 1;
    end;
  end loop;

  return jsonb_build_object(
    'ok', true,
    'checked', v_checked,
    'verified', v_verified,
    'missing', v_missing,
    'error', v_error,
    'remaining_unverified', (
      select count(*)
      from public.wx_image_assets a
      where a.upload_status in ('uploaded', 'exists')
        and a.r2_key is not null
        and a.r2_url is not null
        and a.r2_verified_at is null
    )
  );
end;
$$;

grant execute on function public.verify_wx_image_r2_assets_http_v1(integer) to service_role;
